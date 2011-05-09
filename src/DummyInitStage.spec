#
# This is a spec file, meaning that it is a configuration file for a Stage
# confguration file. A meta-configuration file, if you will. As such, it tells
# the system which parameters should be present in the Stage parameters config
# file section, which ones are optional and their default values. The same for
# the input and output sections as well.
# 
# Spec files are Stage specific and are an optional but integral part of each
# Stage subclass definition.
# 
# Spec files are optional but if present they are used for configuration file
# validation and default value support (not implemented yet).
# 
# Definitions of parameter keys and values.
[output_keys]
    # Clipboard keys are indicated as 
    #     <internal name>: <clipboard key name>[, <object type>]
    pixel_plane = string_list(min=1, max=2)
    bpm_plane = string_list(min=1, max=2)
    error_plane = string_list(min=1, max=2)
    
