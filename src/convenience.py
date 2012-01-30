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
from Pipeline import Pipeline, DEFAULT_LOG_LEVEL, DEFAULT_LOCAL_LOGS
from Step import Step
import utilities
import config_parser




def pipeline_from_config_file(config_file):
    """
    Create a Pipeline instance from a ConfigObj/INI configuration file 
    `config_file` which specifies the Pipeline steps, data directories
    etc.
    """
    # Do we have a spec file? If so, do parameter and input/output key 
    # validation as well. If not keep going.
    spec_file = utilities.find_spec_file(Pipeline)
    
    # Now do the actual parsing and, if we do have a spec file, validate as 
    # well.
    parsed = config_parser.loads(config_file, 
                                 specfile=spec_file)['pipeline']
    
    # Create a Pipeline instance with no steps, we will add them later.
    pipe = Pipeline(name=parsed['name'],
                    system=parsed['system'],
                    log_level=parsed.get('log_level', DEFAULT_LOG_LEVEL),
                    local_logs=parsed.get('local_log_mode', DEFAULT_LOCAL_LOGS))
    
    # The only thing that requires special handling is the steps array. 
    # Here we have to create Step instances of the appropriate class and
    # pass the appropriate Step config file to them.
    # Also, as part of the "steps" list, we have hints on which data each 
    # Step produces and which data it consumes. In order to transfer these
    # pieces of data in-memory between steps we have a simple architecture.
    # We have a dictionary at the Pipeline level where data is put and
    # possibly updated. This is the clipboard. Then before executing each 
    # Step, the data the Step needs in input is put in Step.inbox which
    # is a list. Elements are put in that list in the order they are defined
    # in that Step section of the Pipeline configuration file (inbox 
    # parameter). After the Step completes, data from Step.outbox is 
    # fetched and put in the clipboard. Data in Step.outbox is assumed to 
    # be in the order defined in that Step section of the Pipeline 
    # configuration file (outbox parameter).
    steps = [Step.from_parsed_config(x, pipe) for x in parsed['steps']]
    
    # Finally update the pipe.steps list. We did this so that the Step 
    # instances could make use in their initialization, of whatever they
    # needed to pull from the Pipeline object they belong to.
    pipe.configure(steps)
    return(pipe)




