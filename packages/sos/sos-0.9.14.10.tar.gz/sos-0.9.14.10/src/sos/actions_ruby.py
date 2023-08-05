#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import os
import shutil
import subprocess
import sys
import tempfile

from sos.actions import SoS_Action, SoS_ExecuteScript, collect_input
from sos.eval import interpolate
from sos.targets import UnknownTarget, sos_targets
from sos.utils import env


@SoS_Action(acceptable_args=['script', 'args'])
def ruby(script, args='', **kwargs):
    '''Execute specified script using ruby. This action accepts common action arguments such as
    input, active, workdir, docker_image and args. In particular, content of one or more files
    specified by option input would be prepended before the specified script.'''
    return SoS_ExecuteScript(script, 'ruby', '.rb', args).run(**kwargs)
