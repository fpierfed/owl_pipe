#
# This is a spec file, meaning that it is a configuration file for a Step
# confguration file. A meta-configuration file, if you will. As such, it tells
# the system which parameters should be present in the Step parameters config
# file section, which ones are optional and their default values. The same for
# the input and output sections as well.
# 
# Spec files are Step specific and are an optional but integral part of each
# Step subclass definition.
# 
# Spec files are optional but if present they are used for configuration file
# validation and default value support (not implemented yet).
# 
# Definitions of parameter keys and values.
[parameters]
    # Name/pattern of the FITS file to read.
    file_name = string()
    
    # Name of the Python class to use to represent the FITS file internally.
    class_name = string()



