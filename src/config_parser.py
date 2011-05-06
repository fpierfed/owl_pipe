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
    config = ConfigObj(config_file, configspec=specfile)
    spec = ConfigObj(specfile)
    validator = Validator()
    
    # First validation: make sure that stage_config does not have any spurious
    # section.
    extra_sections = [s for s in config.keys() if s not in spec.keys()]
    if(extra_sections):
        msg = "these sections are unknown: %s." % (', '.join(extra_sections))
        raise(ValidationError(msg))
    
    
    print(spec)
    
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
    ok = config.validate(validator)
    if(not ok):
        # ConfigObj failed but there seems to be no way to know why reliably
        # meaning that flatten_errors does not really work... let's check by 
        # hand.
        for section in spec.keys():
            config_section = config[section]
            spec_section = spec[section]
            
            # Repeat the validation.
            for key in spec_section.keys():
                try:
                    raw_value = config_section[key]
                except KeyError:
                    # So, the key is not optional and it is not there: mistake!
                    msg = 'missing required %s key in section %s.' \
                           % (key, section)
                    raise(ValidationError(msg))
                    
                rule = spec_section[key]
                if(isinstance(rule, list)):
                    rule = ' '.join(rule)
                try:
                    parsed_value = validator.check(rule, raw_value)
                except VdtTypeError:
                     # Wrong type: mistake!
                    msg = '%s=%s in section %s does not satisfy rule %s.' \
                           % (key, raw_value, section, rule)
                    raise(ValidationError(msg))
                
                
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























