#!/usr/bin/python3

"""
Main module for devpipeline_scm.  It provides SCMS, a dictionary with all
detected scm plugins.
"""

import devpipeline_core.plugin

SCMS = devpipeline_core.plugin.query_plugins('devpipeline.scms')
