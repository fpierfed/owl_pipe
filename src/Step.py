# Copyright (C) 2010 Association of Universities for Research in Astronomy(AURA)
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
# 
#     2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
# 
#     3. The name of AURA and its representatives may not be used to
#       endorse or promote products derived from this software without
#       specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY AURA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL AURA BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
"""
Step


"""
import logging

import config_parser
import utilities
from stpipe import DEFAULT_PIPELINE




class StepType(type):
    """
    Simple metaclass to monkeypatch Step and its subclasses: replace __call__
    with whatever the (sub)class run method is (only useful for when users 
    create Steps manually without going through a Pipeline class and its 
    configuration file).
    """
    def __new__(cls, name, bases, attrs):
        if('run_standalone' in attrs.keys()):
            attrs['__call__'] = attrs['run_standalone']
        return(super(StepType, cls).__new__(cls, name, bases, attrs))





class Step(object):
    """
    Step
    """
    __metaclass__ = StepType
    
    @classmethod
    def from_parsed_config(cls, pipeline_config, pipeline):
        """
        Create a Step instance from a parsed Pipeline configuration file 
        `pipeline_config` which specifies the Step steps, data directories as 
        well as the Step configuration file path.
        
        If a file called <self.name>.spec is found in the same directory as the
        Step class source code, then the Step configuration file is validated 
        against the spec file.
        """
        # First understand which Step (sub)class we need to instantiate. The 
        # class name is given in full Python package notation, e.g.
        #   package.subPackage.subsubpackage.className
        # this means that
        #   1. We HAVE to be able to say 
        #       from package.subPackage.subsubpackage import className
        #   2. The resulting Python class MUST be a subclass of Step.
        step_class = utilities.import_class(pipeline_config['python_class'],
                                             subclassof=cls)
        
        # Now, we have the right Python class for our Step, we just need to
        # get to the corresponding config file and we are done.
        step_config = {}
        step_config_file = pipeline_config.get('config_file', None)
        
        # Do we have a spec file? If so, do parameter and input/output key 
        # validation as well. If not keep going.
        step_spec_file = utilities.find_spec_file(step_class)
        if(not step_spec_file):
            pipeline.log.debug("No spec file for Step %s." \
                               % (pipeline_config['name']))
        else:
            pipeline.log.debug("Step %s specfile: %s" \
                               % (pipeline_config['name'], step_spec_file))
        # Now do the actual parsing and, if we do have a spec file, validate as 
        # well.
        if(step_config_file):
            step_config = config_parser.loads(step_config_file, 
                                               specfile=step_spec_file)
            parameters = step_config.get('parameters', {})
        
        # Now we have everything we need to create a Step instance.
        return(step_class(name=pipeline_config['name'], 
                           pipeline=pipeline,
                           input_info=pipeline_config.get('input', []),
                           output_info=pipeline_config.get('output', []),
                           **parameters))
    
    
    
    @classmethod
    def from_config_file(cls, config_file, pipeline=DEFAULT_PIPELINE, name=''):
        """
        Create a Step instance from a ConfigObj/INI configuration file 
        `config_file` which specifies the Pipeline steps, data directories
        etc.
        
        This is used in scripts where users create Steps manually without using
        a Pipeline class. In these cases, we just use teh default Pipeline 
        instance created for us by 
        """
        # Since we do not have a proper Pipeline instance with its configuration
        # file to give us our name, we will generate one, based on the number of
        # Steps already added to `pipeline`.
        if(not name and not [s.name for s in pipeline.steps if s.name == name]):
            name = 'Step%06d' % (len(pipeline.steps))
        
        # Do we have a spec file? If so, do parameter and input/output key 
        # validation as well. If not keep going.
        spec_file = utilities.find_spec_file(cls)
        if(not spec_file):
            pipeline.log.debug("No spec file for Step %s." % ('name'))
        else:
            pipeline.log.debug("Step %s specfile: %s" % (name, spec_file))
        # Now do the actual parsing and, if we do have a spec file, validate as 
        # well.
        config = config_parser.loads(config_file, specfile=spec_file)
        parameters = config.get('parameters', {})
        
        # Create the Step instance.
        step_instance = cls(name=name, 
                            pipeline=pipeline, 
                            input_info=[], 
                            output_info=[],
                            **parameters)
        
        # Add the step instance to pipeline.steps.
        pipeline.steps.append(step_instance)
        
        # Now we have everything we need to create a Step instance.
        return(step_instance)
        
    
    
    def __init__(self, name, pipeline, input_info, output_info, **kws):
        """
        Configure the Step instance.
        """
        self.name = name
        self.pipeline = pipeline
        self.qualified_name = '%s.%s' \
                              % (self.pipeline.qualified_name, self.name)
        self.input_info = input_info
        self.output_info = output_info
        
        # Define the parameters inline.
        for (key, val) in kws.items():
            setattr(self, key, val)
        
        # Get a hold of the clipboard but keep it private.
        self._clipboard = self.pipeline.clipboard
        
        # We need to create a a logger. We choose to reuse the same logger as 
        # self.pipeline but we just change its name to reflect self.name.
        logger = self.pipeline.log.logger
        extra = {'classname': self.qualified_name}
        self.log = logging.LoggerAdapter(logger, extra)
        
        # Log the fact that we have been init-ed.
        self.log.info('%s instance created.' % (self.__class__.__name__))
        return
    
    
    
    def run(self, clipboard_check=True):
        """
        Do any work that we are supposed to do. Before doing the actual work 
        though, grab whatever data is waiting for us in the clipboard and update
        the relevant instance variables with those values. Once we are done 
        processing, put the data back in the clipboard, creating new entries or
        updating old entries as specified in self.output_info.
        """
        self.log.info('Step %s starting.' % (self.name))
        
        # Populate self.inbox from the content of the clipboard. What to put 
        # there is stored in self.input_info.
        self._get_data_from_clipbaord(clipboard_check)
        
        # Run the Step-specific code.
        err = self.process()
        self.log.info('Step %s done (return value: %s).' \
                      % (self.name, str(err)))
        
        # Now update the clipboard.
        self._put_data_to_clipboard(clipboard_check)
        return(err)
    
    
    
    def run_standalone(self, input=None, output=None):
        """
        This is a wrapper around self.run() mainly for the case in which users 
        are building their pipelines by hand without using the Pipeline class. 
        In those cases, we are not provided hints on which instance variables we
        need to pull out of/push to DEFAULT_PIPELINE.clipboard.
        
        The use of `input` and `output` here is the same as self.input_info and 
        self.output_info in the case where a Pipeline instance is used.
        
        Only override self.Input_info and self.output_info if really needed.
        """
        if(input):
            self.input_info = input
        if(output):
            self.output_info = output
        return(self.run())
    
    
    
    def _get_data_from_clipbaord(self, clipboard_check):
        """
        In the pipeline configuration, as part of the "steps" list, we have 
        hints on which data each Step produces and which data it consumes. In 
        order to transfer these pieces of data in-memory between steps we have 
        a simple architecture.
        We have a dictionary at the Pipeline level where data is put and
        possibly updated. This is the clipboard. Before executing each Step, 
        the data the Step needs as input is put in instance variables whose 
        name (and optionally type) are given in the input parameter of the 
        steps section of the pipeline configuration. After the Step completes,
        instance variables of Step (and defined in the output parameter of the 
        same configuration block) are put in the clipboard.
        """
        for clipboard_info in self.input_info:
            # clipboard_info is a tuple. It either has a single element, which 
            # is the name of the clipboard key to fetch, or two elements: the
            # clipboard key (same as before) and the corresponding object type
            # for optional type checking (clipboard_check == True).
            # Either way, put data in self.inbox in the order it is defined in
            # self.input_info.
            if(not utilities.islist_tuple(clipboard_info) or
               not len(clipboard_info) in (0, 1, 2)):
                raise(Exception('Step %s: malformed inbox info %s.' \
                                % (self.name, clipboard_info)))
            if(not clipboard_info):
                # Nothing to do.
                continue
            elif(len(clipboard_info) == 2):
                    [key_name, class_name] = clipboard_info
            elif(len(clipboard_info) == 1):
                key_name = clipboard_info[0]
                class_name = None
            
            # Populate self.inbox but check types first if we need to.
            value = self._clipboard[key_name]
            if(clipboard_check):
                self.log.debug('Checking clipboard input types.')
                if(not class_name):
                    self.log.debug('No class information to do the check.')
                else:
                    cls = utilities.import_class(class_name)
                    assert(isinstance(value, cls))
                    self.log.debug('Clipboard input types are OK.')
            
            # Now create/update the instance variable.
            setattr(self, key_name, value)
        return
    
    
    
    def _put_data_to_clipboard(self, clipboard_check):
        """
        In the pipeline configuration, as part of the "steps" list, we have 
        hints on which data each Step produces and which data it consumes. In 
        order to transfer these pieces of data in-memory between steps we have 
        a simple architecture.
        We have a dictionary at the Pipeline level where data is put and
        possibly updated. This is the clipboard. Before executing each Step, 
        the data the Step needs as input is put in instance variables whose 
        name (and optionally type) are given in the input parameter of the 
        steps section of the pipeline configuration. After the Step completes,
        instance variables of Step (and defined in the output parameter of the 
        same configuration block) are put in the clipboard.
        """
        for clipboard_info in self.output_info:
            # clipboard_info is a tuple. It either has a single element, which 
            # is the name of the clipboard key to fetch, or two elements: the
            # clipboard key (same as before) and the corresponding object type
            # for optional type checking (clipboard_check == True).
            # Either way, put data in self.inbox in the order it is defined in
            # self.input_info.
            if(not (isinstance(clipboard_info, tuple) or 
                    isinstance(clipboard_info, list)) or
               not len(clipboard_info) in (0, 1, 2)):
                raise(Exception('Step %s: malformed output info %s.' \
                                % (self.name, clipboard_info)))
            if(not clipboard_info):
                # Nothing to do.
                continue
            elif(len(clipboard_info) == 2):
                    [key_name, class_name] = clipboard_info
            elif(len(clipboard_info) == 1):
                key_name = clipboard_info[0]
                class_name = None
            
            # Fetch value from self.<key_name> but check types first if we need 
            # to.
            value = getattr(self, key_name)
            if(clipboard_check):
                self.log.debug('Checking clipboard output types.')
                if(not class_name):
                    self.log.debug('No class information to do the check.')
                else:
                    cls = utilities.import_class(class_name)
                    assert(isinstance(value, cls))
                    self.log.debug('Clipboard output types are OK.')
            
            # Now update the clipboard.
            self._clipboard[key_name] = value
        return
    
    
    
    def process(self):
        """
        This is where real work happens. Every Step subclass has to override
        this method. The default behaviour is to raise a NotImplementedError
        exception.
        """
        raise(NotImplementedError('Steps have to override process().'))








        































