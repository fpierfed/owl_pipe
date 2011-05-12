# 
# Pipeline spec file (in ConfigObj/INI format).
# 
[pipeline]
    # Name is a string set to whatever you want to call your pipeline. It 
    # is used to identify the pipeline in the logs.
    name = string()
    
    # System is a string that can be used to logically group pipelines 
    # together. Again mainly used in logs.
    system = string()
    
    # Log level is a string that determines the verbosity of logs. 
    # Supported values are those of the Python logging module (i.e. 
    # "CRITICAL", "DEBUG", "ERROR", "FATAL", "INFO", "WARNING").
    log_level = string()
    
    # If local_log_mode is true, then the logs are written to file in 
    # the work directory. Otherwise they are printed to STDOUT only.
    local_log_mode = boolean(default=False)
    
    # Now the stage definitions, in order of execution.
    [[stages]]
        [[[__many__]]]
        config_file = string()
        python_class = string()
        input = force_list(default=list())
        output = force_list(default=list())


