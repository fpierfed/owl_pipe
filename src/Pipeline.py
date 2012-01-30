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
Pipeline


"""
import logging


import config_parser
import utilities






# Constants/Default Values.
DEFAULT_PIPELINE_NAME = 'DefaultPipeline'
DEFAULT_SYSTEM_NAME = 'DefaultSystem'
DEFAULT_LOG_LEVEL = 'DEBUG'
DEFAULT_LOCAL_LOGS = False



class Pipeline(object):
    """
    Pipeline
    """
    def __init__(self, 
                 name=DEFAULT_PIPELINE_NAME, 
                 system=DEFAULT_SYSTEM_NAME, 
                 log_level=DEFAULT_LOG_LEVEL, 
                 local_logs=DEFAULT_LOCAL_LOGS):
        """
        Configure the Pipeline instance.
        """
        self.name = name
        self.system = system
        self.qualified_name = '%s.%s' % (self.system, self.name)
        self.log_level = getattr(logging, log_level)
        self.local_logs = local_logs
        self.steps = []
        # The clipboard is a dictionary for input and output data (consumed and
        # produced by Steps). Steps get items from the clipboard, work on 
        # them and then put their products back in the clipboard. What to
        # get from the clipboard is defined in the Step configuration file in 
        # the input_keys dictionary. What to put back is defined in the Step 
        # configuration file, in the output_keys dictionary.
        self.clipboard = {}
        
        # Now create a logger.
        logger = logging.getLogger(self.qualified_name)
        logger.setLevel(self.log_level)
        extra = {'classname': self.qualified_name}
        
        fmt = '%(asctime)s - %(classname)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt)
        
        if(local_logs):
            handler = logging.FileHandler('%s.log' % (self.qualified_name))
        else:
            handler = logging.StreamHandler()
        handler.setLevel(self.log_level)
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        self.log = logging.LoggerAdapter(logger, extra)
        
        # Log the fact that we have been init-ed.
        self.log.info('Pipeline instance created.')
        return
    
    
    def configure(self, steps):
        """
        Configure the Pipeline instance by assigining a list of Steps to it.
        Do any further config needed once the Steps have themselves been 
        initialized.
        """
        self.steps = steps
        
        self.log.info('Pipeline configured and steps added.')
        return
    
    
    def run(self):
        """
        Execute each Step in self.steps in turn and ten exit.
        """
        for step in self.steps:
            self.log.info('Starting Step %s' % (step.name))
            error = step.run()
            if(error):
                raise(Exception('Step %s exited with error code %d' \
                      % (step.name, error)))
        return
    

    
    
    
    
    

        
