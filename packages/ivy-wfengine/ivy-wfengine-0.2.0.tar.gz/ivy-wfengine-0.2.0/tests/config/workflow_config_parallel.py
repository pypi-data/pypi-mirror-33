# Copyright (C) 2013 ETH Zurich, Institute for Astronomy

'''
Created on Mar 5, 2014

author: jakeret
'''
# from ivy.config import base_config
from ivy.plugin.parallel_plugin_collection import ParallelPluginCollection

backend = "sequential"
cpu_count = 1
valuesMin = 1
valuesMax = 10

plugins = ["tests.plugin.simple_plugin",
           ParallelPluginCollection(
                                    ["tests.plugin.simple_square_plugin"],
                                    "tests.plugin.range_map_plugin",
                                    "tests.plugin.sum_reduce_plugin"),
           "tests.plugin.simple_plugin"
           ]
