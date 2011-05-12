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
Our configuration files are ConfigObj/INI files.
"""
from configobj import ConfigObj
from validate import Validator, VdtTypeError






class ValidationError(Exception): pass




def loads(config_file, specfile=None):
    """
    Read the input `raw_text` and return a dictionary with the parsed 
    configuration.
    """
    if(not specfile):
        config = simple_parse(config_file)
    else:
        config = validated_parse(config_file, specfile)
    
    # Add a 'name' key to each of the 'stages' dictionaries and set its value to
    # the corresponding key in the original 'stages' entry. This only if we are 
    # parsing a pipeline config file, that is. Kind of messy :-(
    if(config.has_key('pipeline')):
        return(_pipeline_config_fix(config))
    return(config)



def validated_parse(config_file, specfile):
    """
    Parse config_file, in INI format, and do validation with the provided 
    specfile.
    """
    config = ConfigObj(config_file, configspec=specfile, raise_errors=True)
    spec = ConfigObj(specfile)
    validator = Validator()
    
    # First validation: make sure that stage_config does not have any spurious
    # section.
    extra_sections = [s for s in config.keys() if s not in spec.keys()]
    if(extra_sections):
        msg = "these sections are unknown: %s." % (', '.join(extra_sections))
        raise(ValidationError(msg))
    
    # Now, make sure that we do not have spurious stuff in each section.
    for section in spec.keys():
        config_section = config[section]
        spec_section = spec[section]
        
        extra_keys = [k for k in config_section.keys() \
                      if k not in spec_section.keys()]
        if(extra_keys):
            msg = "These entries in the %s section are unknown: %s" \
                  % (section, ', '.join(extra_keys))
            raise(ValidationError(msg))
    
    # Finally do the ConfigObj validation and hope that nothing happens.
    # No we do not because it does not work!
    ok = config.validate(validator)
    if(not ok):
        raise(Exception('Unable to parse %s and validate against %s' \
                        % (config_file, specfile)))
    
    # Now, parse input and output in the Stage definition by hand.
    if(config.has_key('pipeline')):
        stage_configs =  config['pipeline']['stages']
        for stage_name in stage_configs.keys():
            stage_config = stage_configs[stage_name]
            
            input = [[xx.strip() for xx in x.split(',')] 
                     for x in stage_config.get('input', [])]
            stage_config['input'] = input
            
            output = [x.split(',') for x in stage_config.get('output', [])]
            stage_config['output'] = output
    return(config)



def simple_parse(config_file):
    """
    Do simple parsing and home-brewed type interference.
    """
    config = ConfigObj(config_file)
    config.walk(string_to_python_type)
    return(config)




def _pipeline_config_fix(config):
    """
    Add a 'name' key to each of the 'stages' dictionaries and set its value to
    the corresponding key in the original 'stages' entry. This only if we are 
    parsing a pipeline config file, that is. Kind of messy :-(
    """
    for stage_name in config['pipeline']['stages']:
        config['pipeline']['stages'][stage_name]['name'] = stage_name
    config['pipeline']['stages'] = config['pipeline']['stages'].values()
    return(config)



def string_to_python_type(section, key):
    """
    Do blind type inferring.
    """
    # We parse scalars and lists.
    val = section[key]
    if(isinstance(val, list)):
        typed_val = [_parse(x) for x in val]
    else:
        typed_val = _parse(val)
    section[key] = typed_val
    return



def _parse(val):
    """
    Do the actual parsing of scalar strings into scalar python types.
    """
    if(val.lower() == 'true'):
        return(True)
    elif(val.lower() == 'false'):
        return(False)
    try:
        return(int(val))
    except:
        pass
    try:
        return(float(val))
    except:
        pass
    return(str(val))























