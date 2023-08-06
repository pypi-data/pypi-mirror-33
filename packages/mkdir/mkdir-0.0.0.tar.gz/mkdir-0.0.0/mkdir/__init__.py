#!/usr/bin/env python
import os
from public import public


@public
def mkdir(path):
    if path and not os.path.exists(path):
        os.makedirs(path)
