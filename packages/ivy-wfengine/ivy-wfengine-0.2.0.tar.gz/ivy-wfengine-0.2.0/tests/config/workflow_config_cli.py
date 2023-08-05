# Copyright (C) 2013 ETH Zurich, Institute for Astronomy

'''
Created on Mar 5, 2014

author: jakeret
'''
from ivy.config import base_config
from ivy.loop import Loop

plugins = Loop(["tests.plugin.simple_plugin",
                "tests.plugin.simple_plugin"
                ])
