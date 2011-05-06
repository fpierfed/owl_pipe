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
[parameters]
    # The command to execute. Required and no default value assigned.
    command = string()
    
    # Its arguments. It is a list and it might be empty.
    arguments = string_list(min=0, default=[])
    
    # Do we want to log STDOUT?
    log_stdout = boolean(default=True)
    
    
    # Do we want to log STDERR?
    log_stderr = boolean(default=True)
    
    # Pass the command exit code through?
    exitcode_passthrough = boolean(default=True)
