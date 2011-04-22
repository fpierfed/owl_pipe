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
import subprocess
import traceback

from Stage import Stage





class SystemCallStage(Stage):
    """
    Execute the command given in the configuration file in a system call and
    potentially log the command STDOUT and/or STDERR. If requested, the exit 
    code of the Stage process method is that of the command being executed. 
    Otherwise it is whether or not the system call itself suceeded.
    """
    def process(self):
        """
        Execute the command given in the parameters section of teh configuration
        file in a system call. These are the relevant parameters:
            self.command: the command to execute. This is the same as executable
                in subprocess.Popen()
            self.arguments: the argument list to self.command. It can be empty.
            self.log_stdout: boolean. If True, pipe the command STDOUT to 
                self.log
            self.log_stderr: boolean. If True, pipe the command STDERR to 
                self.log
            self.exitcode_passthrough: boolean. If True the return value of 
                self.process() is the exit code of self.process. If False it is
                the return code of the system call itself (usually 0). Setting 
                this parameter to False is useful in cases where self.command 
                could fail but we do not want the Pipeline to stop.
        """
        cmd_str = '%s %s' % (self.command, ' '.join(self.arguments))
        
        # Start the process and wait for it to finish.
        self.log.info('Starting "%s"' % (cmd_str))
        try:
            p = subprocess.Popen(args=[self.command, ] + self.arguments,
                                 stdin=None,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=False)
            err = p.wait()
        except:
            # We got an exception. This is a problem unless 
            # self.exitcode_passthrough == False, in whiuch case we do not care.
            msg = 'The execution of "%s" failed with an exception: \n%s' \
                  % (cmd_str, traceback.format_exc())
            self.log.info(msg)
            
            if(not self.exitcode_passthrough):
                self.log.info('exitcode_passthrough=false: errors are ignored.')
                return(0)
            else:
                raise(Exception(msg))
        
        self.log.info('"%s" command done.' % (self.command))
        
        # Log STDOUT/ERR if we are asked to do so.
        if(self.log_stdout):
            self.log.info('"%s" STDOUT: "%s"' % (self.command, p.stdout.read()))
        if(self.log_stderr):
            self.log.info('"%s" STDERR: "%s"' % (self.command, p.stderr.read()))
        
        # Return err or 0?
        if(self.exitcode_passthrough):
            return(err)
        return(0)








