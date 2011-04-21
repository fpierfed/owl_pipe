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
from Stage import Stage
import utilities




class DummyInitStage(Stage):
    def process(self):
        # Handle self.output_info
        for (key, class_name) in self.output_info.items():
            # Import class_name.
            cls = utilities.import_class(class_name)
            
            # Create a dummy instance of cls.
            dummy_object = cls()
            
            # Write it in the clipboard.
            self.clipboard[key] = dummy_object
            
            # Log what we did.
            self.log.info('Added a new instance of %s to the clipboard as %s' \
                          % (class_name, key))
        return



class DummyStage(Stage):
    def process(self):
        # Do nothing.
        return



class AnotherDummyStage(Stage):
    def process(self):
        # Handle self.input_info
        for (key, class_name) in self.input_info.items():
            # Log what we found.
            self.log.info('Found an instance of %s in the clipboard as %s' \
                          % (self.clipboard[key].__class__.__name__, key))
        
        # Handle self.output_info
        for (key, class_name) in self.output_info.items():
            # Import class_name.
            cls = utilities.import_class(class_name)
            
            # Create a dummy instance of cls.
            dummy_object = cls()
            
            # Write it in the clipboard.
            self.clipboard[key] = dummy_object
            
            # Log what we did.
            self.log.info('Added a new instance of %s to the clipboard as %s' \
                          % (class_name, key))
        return
