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
from Stage import Stage



class Pipeline(object):
    """
    Pipeline
    """
    @classmethod
    def from_config_file(cls, config_file):
        """
        Create a Pipeline instance from a JSON configuration file 
        `configFile` which specifies the Pipeline stages, data directories
        etc.
        """
        parsed = config_parser.loads(config_file)['pipeline']
        
        # Create a Pipeline instance with no stages, we will add them later.
        pipe = cls(name=parsed['name'],
                   system=parsed['system'],
                   log_level=parsed.get('log_level', 'DEBUG'),
                   local_logs=parsed.get('local_log_mode', False))
        
        # The only thing that requires special handling is the stages array. 
        # Here we have to create Stage instances of the appropriate class and
        # pass the appropriate Stage config file to them.
        stages = [Stage.from_parsed_config(x, pipe) for x in parsed['stages']]
        
        # Finally update the pipe.stages list. We did this so that the Stage 
        # instances could make use in their initialization, of whatever they
        # needed to pull from the Pipeline object they belong to.
        pipe.configure(stages)
        return(pipe)
        
    
    def __init__(self, name, system, log_level, local_logs):
        """
        Configure the Pipeline instance.
        """
        self.name = name
        self.system = system
        self.qualified_name = '%s.%s' % (self.system, self.name)
        self.log_level = getattr(logging, log_level)
        self.local_logs = local_logs
        self.stages = []
        # The clipboard is a dictionary for input and output data (consumed and
        # produced by Stages). Stages get items from the clipboard, work on 
        # them and then put their products back in the clipboard. What to
        # get from the clipboard is defined in the Stage configuration file in 
        # the input_keys dictionary. What to put back is defined in the Stage 
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
    
    
    def configure(self, stages):
        """
        Configure the Pipeline instance by assigining a list of Stages to it.
        Do any further config needed once the Stages have themselves been 
        initialized.
        """
        self.stages = stages
        
        self.log.info('Pipeline configured and stages added.')
        return
    
    
    def run(self):
        """
        Execute each Stage in self.stages in turn and ten exit.
        """
        for stage in self.stages:
            self.log.info('Starting Stage %s' % (stage.name))
            error = stage.run()
            if(error):
                raise(Exception('Stage %s exited with error code %d' \
                      % (stage.name, error)))
        return


        
