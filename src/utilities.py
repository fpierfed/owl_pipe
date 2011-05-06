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
Utilities
"""
import inspect
import os
import sys

import config_parser






class ValidationError(Exception): pass





def import_class(full_name, subclassof=None):
    """
    Import the Python class `full_name` given in full Python package format
    e.g. 
        package.another_package.class_name
    Return the imported class. Optionally, if `subclassof` is not None and is 
    a Python class, make sure that the imported class is a subclass of 
    `subclassof`.
    """
    # Understand which class we need to instantiate. The class name is given in
    # full Python package notation, e.g.
    #   package.subPackage.subsubpackage.className
    # in the input parameter `full_name`. This means that
    #   1. We HAVE to be able to say 
    #       from package.subPackage.subsubpackage import className
    #   2. If `subclassof` is defined, the newly imported Python class MUST be a
    #      subclass of `subclassof`, which HAS to be a Python class.
    
    full_name = full_name.strip()
    package_name, class_name = str(full_name).rsplit('.', 1)
    imported = __import__(package_name, globals(), locals(), [class_name, ])
    
    # Now we can have two situation and we try and support both:
    #   1. What we call imported is really a module in which class_name is
    #      defined.
    #   2. imported, by virtue of whatever module __init__.py magic, is
    #      already the Python class we want.
    # Is imported a module?
    if(isinstance(imported, type(sys))):
        stage_class = getattr(imported, class_name)
    else:
        stage_class = imported
    
    if(subclassof and not issubclass(stage_class, subclassof)):
        msg = 'Class %s from package %s is not a subclass of %s' \
              % (class_name, package_name, subclassof.__name__)
        raise(NotImplementedError(msg))
    return(stage_class)



def get_spec_file_path(stage_class):
    """
    Given a Stage (sub)class, divine and return the full path to the 
    corresponding spec file. Use the fact that by convention, the spec file is 
    in the same directory as the `stage_class` source file. It has the name of 
    the Stage (sub)class and extension .spec.
    """
    stage_source_file = os.path.abspath(inspect.getfile(stage_class))
    root = os.path.splitext(stage_source_file)[0]
    return(root + '.spec')



def find_spec_file(stage_class):
    """
    Return True is a file named <stage_class.__name__>.spec exists in the same
    director as <stage_class.__name__>.py. Return False otherwise.
    """
    return(os.path.exists(get_spec_file_path(stage_class)))




def validate_stage_config(stage_class, stage_config):
    """
    Given a Stage (sub)class `stage_class` and a parsed Stage configuration file
    `stage_config`, make sure that everything makes sense according to the Stage
    spec file.
    
    If a spec file is found and the config file validates (meaning that 
    `parameters`, `input` and `output` validate), then return True.
    If a spec file is not found, then return False.
    If a spec file is found but there is a validation error, raise an exception.
    """
    # Read the spec file in, parse it and understand what we nee to do. If the
    # spec file cannot be found, oh well... return False.
    spec_file = get_spec_file_path(stage_class)
    if(not os.path.exists(spec_file)):
        return(False)
    
    # Parse the spec file.
    constraints = config_parser.loads(open(spec_file).read())
    sections = ('parameters', 'input_keys', 'output_keys')
    
    # First validation: make sure that stage_config does not have any spurious
    # section.
    extra_sections = [s for s in stage_config.keys() if s not in sections]
    if(extra_sections):
        msg = "these sections in the %s configuration file are unknown: %s." \
              % (stage_class.__name__, ', '.join(extra_sections))
        raise(ValidationError(msg))
    
    
    # TODO: Default value support.
    # Now, one by one, make sure each section validates.
    for section in sections:
        constraint = constraints.get(section, {})
        config = stage_config.get(section, {})
        
        # First make sure that we have no keys in in the config that are not in
        # the spec file.
        extra_keys = [k for k in config.keys() if k not in constraint.keys()]
        if(extra_keys):
            msg = "These entries in the %s section are unknown: %s" \
                  % (section, ', '.join(extra_keys))
            raise(ValidationError(msg))
        
        # Now make sure that if a key is required, it is there. Also if a key is
        # there, make sure that it is of the correct type.
        for key in constraint.keys():
            key_constraints = constraint[key]
            
            # Is the key there if it should be?
            if(not key in config.keys() and not key_constraints['optional']):
                # So, the key is not optional and it is not there: mistake!
                msg = 'missing required %s key in section %s.' % (key, section)
                raise(ValidationError(msg))
            
            # Now, make sure that if the key is there, it is of the right type.
            key_type = type(config[key]).__name__
            if(key_type == 'unicode'):
                key_type = 'str'
            if(not key_type == key_constraints['type']):
                # Wrong type: mistake!
                msg = '%s key in section %s if of type %s instead of %s.' \
                      % (key, section, key_type, key_constraints['type'])
                raise(ValidationError(msg))
        
    return(True)


















































