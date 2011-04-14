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
import sys







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


