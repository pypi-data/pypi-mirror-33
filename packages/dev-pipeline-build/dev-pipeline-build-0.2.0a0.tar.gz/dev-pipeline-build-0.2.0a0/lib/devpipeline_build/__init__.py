#!/usr/bin/python3

"""
Root module for the build plugin.  It provides the BUILDERS dictionary, which
contains every builder plugin.
"""

import devpipeline_core.plugin

BUILDERS = devpipeline_core.plugin.query_plugins('devpipeline.builders')
