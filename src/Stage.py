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
Stage


"""
import logging

import config_parser
import utilities




class Stage(object):
    """
    Stage
    """
    @classmethod
    def from_parsed_config(cls, pipeline_config, pipeline):
        """
        Create a Stage instance from a JSON configuration file 
        `configFile` which specifies the Stage stages, data directories
        etc.
        
        If a sile called <self.name>.spec is found in the same directory as the
        Stage class source code, then the configuration file is validated 
        against the spec file.
        """
        # First understand which Stage (sub)class we need to instantiate. The 
        # class name is given in full Python package notation, e.g.
        #   package.subPackage.subsubpackage.className
        # this means that
        #   1. We HAVE to be able to say 
        #       from package.subPackage.subsubpackage import className
        #   2. The resulting Python class MUST be a subclass of Stage.
        stage_class = utilities.import_class(pipeline_config['python_class'],
                                             subclassof=cls)
        
        # Now, we have the right Python class for our Stage, we just need to
        # get to the corresponding config file and we are done.
        stage_config = {}
        stage_config_file = pipeline_config.get('config_file', None)
        
        # Do we have a spec file? If so, do parameter and input/output key 
        # validation as well. If not keep going.
        stage_spec_file = utilities.find_spec_file(stage_class)
        if(not stage_spec_file):
            pipeline.log.debug("No spec file for Stage %s." \
                               % (pipeline_config['name']))
        else:
            pipeline.log.debug("Stage %s specfile: %s" \
                               % (pipeline_config['name'], stage_spec_file))
        # Now do the actual parsing and, if we do have a spec file, validate as 
        # well.
        if(stage_config_file):
            stage_config = config_parser.loads(stage_config_file, 
                                               specfile=stage_spec_file)
            parameters = stage_config.get('parameters', {})
            input = stage_config.get('input_keys', {})
            output = stage_config.get('output_keys', {})
        
        # Now we have everything we need to create a Stage instance.
        return(stage_class(name=pipeline_config['name'], 
                           pipeline=pipeline,
                           input_info=input,
                           output_info=output,
                           **parameters))
        
    
    def __init__(self, name, pipeline, input_info, output_info, **kws):
        """
        Configure the Stage instance.
        """
        self.name = name
        self.pipeline = pipeline
        self.qualified_name = '%s.%s' \
                              % (self.pipeline.qualified_name, self.name)
        self.input_info = input_info
        self.output_info = output_info
        
        for (key, val) in kws.items():
            setattr(self, key, val)
        
        # Get a hold of the clipboard.
        self.clipboard = self.pipeline.clipboard
        
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
        Do any work that we are supposed to do.
        """
        self.log.info('Stage %s starting.' % (self.name))
        
        if(clipboard_check):
            self.log.debug('Checking clipboard input types.')
            
            for (var_name, (key_name, class_name)) in self.input_info.items():
                # Now, var_name is just the name we should use internally and so
                # it has no meaning outside of this instance. What we care about
                # are the classes.
                cls = utilities.import_class(class_name)
                assert(isinstance(self.clipboard[key_name], cls))
            self.log.debug('Clipboard input types are OK.')
        
        
        # Run the Stage-specific code.
        err = self.process()
        self.log.info('Stage %s done (return value: %s).' \
                      % (self.name, str(err)))
        
        
        if(clipboard_check):
            self.log.debug('Checking clipboard output types.')
            
            for (var_name, clipboard_info) in self.output_info.items():
                # Clipboard_info is either a one or two element list. In the 
                # first case, it is simply the name of the clipboard key. In the
                # second case, it is the name of the key and the name of the 
                # class of the data to be put in that key.
                if(len(clipboard_info) == 2):
                    [key_name, class_name] = clipboard_info
                elif(len(clipboard_info) == 1):
                    key_name = clipboard_info[0]
                    print(var_name, clipboard_info)
                    self.log.debug('No class info to validate %s.' % (key_name))
                    continue
                else:
                    print(clipboard_info)
                    raise(Exception('Malformed configuration file.'))
                
                # Now, var_name is just the name we should use internally and so
                # it has no meaning outside of this instance. What we care about
                # are the classes.
                cls = utilities.import_class(class_name)
                assert(isinstance(self.clipboard[key_name], cls))
                self.log.debug('Clipboard %s type OK.' % (key_name))
        return(err)
    
    
    def process(self):
        """
        This is where real work happens. Every Stage subclass has to override
        this method. The default behaviour is to raise a NotImplementedError
        exception.
        """
        raise(NotImplementedError('Stages have to override process().'))








        































