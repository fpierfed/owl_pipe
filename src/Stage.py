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
        config = {}
        config_file = pipeline_config.get('config_file', None)
        if(config_file):
            config = config_parser.loads(open(config_file).read())
            parameters = config.get('parameters', {})
            input = config.get('input', {})
            output = config.get('output', {})
        
        # Turn the keys in config to strings.
        parameters = dict([(str(k), v) for (k, v) in parameters.items()])
        input = dict([(str(k), v) for (k, v) in input.items()])
        output = dict([(str(k), v) for (k, v) in output.items()])
        
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
            self.log.debug('Checking clipboard input keys and object types.')
            for key in self.input_info:
                # Make sure that the clipboard has the key.
                assert(self.clipboard.has_key(key))
                # Make sure that the corresponding object is of a class that
                # we can import.
                cls = utilities.import_class(self.input_info[key])
                assert(isinstance(self.clipboard[key], cls))
            self.log.debug('Clipboard input keys and object types are OK.')
        
        # Run the Stage-specific code.
        self._run()
        
        self.log.info('Stage %s done.' % (self.name))
        return
    
    
    def _run(self):
        """
        This is where real work happens. Every Stage subclass has to override
        this method. The default behaviour is to raise a NotImplementedError
        exception.
        """
        raise(NotImplementedError('Stages have to override the _run method.'))








        































