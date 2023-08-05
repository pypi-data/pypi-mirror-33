# Copyright (C) 2013 ETH Zurich, Institute for Astronomy

"""
Tests for `ivy.plugin.parallel_plugin_collection ` module.

author: jakeret
"""
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest

from ivy.plugin.parallel_plugin_collection import ParallelPluginCollection
from ivy import context
from ivy.workflow_manager import WorkflowManager
from ivy.context import ctx
from tests.ctx_sensitive_test import ContextSensitiveTest
from tests.plugin import range_map_plugin
from tests.plugin import sum_reduce_plugin
from ivy.exceptions.exceptions import InvalidLoopException
from ivy.exceptions.exceptions import InvalidAttributeException

PLUGIN_NAME = "tests.plugin.simple_square_plugin"

class TestParallelPluginCollection(ContextSensitiveTest):

    def test_setup(self):
        try:
            ParallelPluginCollection(None, "tests.plugin.range_map_plugin")
            pytest.fail("No list provided")
        except InvalidLoopException:
            assert True

        try:
            ParallelPluginCollection([], None)
            pytest.fail("No map plugin provided")
        except InvalidAttributeException:
            assert True

    def test_sequential(self):
        ctx = context.ctx()
        ctx.timings = []
        ctx.params = context._createImmutableCtx(backend="sequential",
                                                 valuesMin = 1,
                                                 valuesMax = 10)


        mapPlugin = range_map_plugin.Plugin(ctx)
        pluginList = [PLUGIN_NAME]
        reducePlugin = sum_reduce_plugin.Plugin(ctx)

        parallelPluginCollection = ParallelPluginCollection(pluginList, mapPlugin, reducePlugin)
        parallelPluginCollection()
        assert ctx.valuesSum == 285

    def test_multiprocessing(self):
        ctx = context.ctx()
        ctx.timings = []
        ctx.params = context._createImmutableCtx(backend="multiprocessing",
                                                 cpu_count=8,
                                                 valuesMin = 1,
                                                 valuesMax = 10)

        mapPlugin = range_map_plugin.Plugin(ctx)
        pluginList = [PLUGIN_NAME]
        reducePlugin = sum_reduce_plugin.Plugin(ctx)

        parallelPluginCollection = ParallelPluginCollection(pluginList, mapPlugin, reducePlugin)
        parallelPluginCollection()
        assert ctx.valuesSum == 285
#
    def test_parallel_workflow(self):
        args = ["--backend=multiprocessing",
                "--cpu-count=1",
                "tests.config.workflow_config_parallel"]

        mgr = WorkflowManager(args)
        mgr.launch()
        assert ctx().valuesSum == 285


    def teardown(self):
        #tidy up
        print("tearing down " + __name__)
        pass


if __name__ == '__main__':
#     pytest.main()
    test = TestParallelPluginCollection()
    test.test_sequential()

