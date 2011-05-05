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
Our configuration files are JSON with two differences:
    1. Comments which start which start with // and go to the end of the line.
    2. Only strings have double quotes, not variables names not dictionary keys.
"""
# Try and import the json module. If that fails (maybe because we are on Python
# 2.5, import simplejson as json. If that fails as well... too bad!
try:
    import json
except:
    import simplejson as json
import re



# Constants
# See also http://docs.python.org/reference/lexical_analysis.html for valid
# Python variable names.
ADD_QUOTES_SRC = re.compile('([a-zA-Z_][a-zA-Z_0-9]*)(\s*:.+)')
ADD_QUOTES_DST = r'"\1"\2'




def loads(raw_text, *args, **kws):
    """
    Massage raw_text so that it is valid JSON.
    """
    # Massage raw_test so that it is valid JSON and then pass it to json.loads.
    json_text = ''
    
    for raw_line in raw_text.split('\n'):
        # Remove comments
        tokens = raw_line.split('//', 1)
        code = tokens[0]
        if(len(tokens) == 2):
            code, comment = tokens
        
        code = code.rstrip()
        if(not code):
            continue
        
        # Quote keywords.
        json_line = ADD_QUOTES_SRC.sub(ADD_QUOTES_DST, code)
        
        # Make sure that we still have a \n at the end.
        if(not json_line.endswith('\n')):
            json_line += '\n'
        
        json_text += json_line
    return(json.loads(json_text, *args, **kws))
