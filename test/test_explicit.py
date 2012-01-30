#!/usr/bin/env python
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

from stpipe.TestSteps import *
from stpipe.FitsIOSteps import *
from stpipe.SystemCallStep import *



# Create a pipeline by simply stringing together individual Steps. In this case
# there is no Pipeline class per se: the pipeline is this script.
kwds = {'config_file': 'steps/init_step.cfg', 'name': 'InitStep'}
init_step = DummyInitStep.from_config_file(**kwds)

kwds = {'config_file': 'steps/some_imageio_step.cfg', 
        'name': 'ReadFitsImageStep'}
read_fits_step = FitsImageIOStep.from_config_file(**kwds)

kwds = {'config_file': 'steps/some_step.cfg', 'name': 'SomeStep'}
some_step = DummyStep.from_config_file(**kwds)

kwds = {'config_file': 'steps/some_other_step.cfg', 'name': 'SomeOtherStep'}
some_other_step = AnotherDummyStep.from_config_file(**kwds)
             
kwds = {'config_file': 'steps/some_systemcall_step.cfg', 
        'name': 'SomeSystemCallStep'}
syscall_step = SystemCallStep.from_config_file(**kwds)


# Now run these steps in order on some data.
input = []
output=[('image', 'stpipe.models.Image'), 
        ('bpm', 'stpipe.models.Image'), 
        ('variance', 'stpipe.models.Image')]
init_step(input, output)

input = []
output=[('image', 'stpipe.models.Image'), ]
read_fits_step(input, output)

input = []
output = []
some_step(input, output)

input=[('image', 'stpipe.models.Image'), 
       ('bpm', 'stpipe.models.Image'), 
       ('variance', 'stpipe.models.Image')]
output=[('proc_image', 'stpipe.models.Image'), 
        ('proc_bpm', 'stpipe.models.Image'), 
        ('proc_variance', 'stpipe.models.Image')]
some_other_step(input, output)

input = []
output = []
syscall_step(input, output)

