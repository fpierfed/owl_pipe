//
// This is a spec file, meaning that it is a configuration file for a Stage
// confguration file. A meta-configuration file, if you will. As such, it tells
// the system which parameters should be present in the Stage parameters config
// file section, which ones are optional and their default values. The same for
// the input and output sections as well.
// 
// Spec files are Stage specific and are an optional but integral part of each
// Stage subclass definition.
// 
// Spec files are optional but if present they are used for configuration file
// validation and default value support (not implemented yet).
// 
{
    // Definitions of parameter keys and values.
    parameters: {
        // The command to execute. Required and no default value assigned.
        command: {
            // Python type.
            type: "str",
            // Human readable parameter description.
            description: "the command to execute",
            // Optional?
            optional: false
        },
        
        // Its arguments. It is a list and it might be empty.
        arguments: {
            // Python type.
            type: "list",
            // Human readable parameter description.
            description: "The (optional) arguments to command.",
            // Optional?
            optional: true,
            // Default value in case the parameter is omitted from the config.
            default: []
        },
        
        // Do we want to log STDOUT?
        log_stdout: {
            // Python type.
            type: "bool",
            // Human readable parameter description.
            description: "If True, STDOUT is piped to the Stage log file.",
            // Optional?
            optional: true,
            // Default value in case the parameter is omitted from the config.
            default: true
        },
        
        
        // Do we want to log STDERR?
        log_stderr: {
            // Python type.
            type: "bool",
            // Human readable parameter description.
            description: "If True, STDERR is piped to the Stage log file.",
            // Optional?
            optional: true,
            // Default value in case the parameter is omitted from the config.
            default: true
        },
        
        // Pass the command exit code through?
        exitcode_passthrough: {
            // Python type.
            type: "bool",
            // Human readable parameter description.
            description: "If True, the exit code of the Stage is that of command.",
            // Optional?
            optional: true,
            // Default value in case the parameter is omitted from the config.
            default: true
        }
    }
}
