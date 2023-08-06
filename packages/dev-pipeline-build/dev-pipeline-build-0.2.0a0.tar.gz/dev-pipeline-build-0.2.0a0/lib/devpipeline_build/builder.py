#!/usr/bin/python3
"""This modules aggregates the available builders that can be used."""

import os.path
import os

import devpipeline_core.toolsupport

import devpipeline_build


def _nothing_builder(current_config, common_wrapper):
    # Unused variables
    del current_config
    del common_wrapper

    class _NothingBuilder:
        def configure(self, src_dir, build_dir):
            # pylint: disable=missing-docstring
            pass

        def build(self, build_dir):
            # pylint: disable=missing-docstring
            pass

        def install(self, build_dir, path):
            # pylint: disable=missing-docstring
            pass

    return _NothingBuilder()


_NOTHING_BUILDER = (_nothing_builder, "Do nothing.")


def _make_builder(current_target, common_wrapper):
    """
    Create and return a Builder for a component.

    Arguments
    component - The component the builder should be created for.
    """
    return devpipeline_core.toolsupport.tool_builder(
        current_target["current_config"], "build", devpipeline_build.BUILDERS,
        current_target, common_wrapper)


class SimpleBuild(devpipeline_core.toolsupport.SimpleTool):

    """This class does a simple build - configure, build, and install."""

    def __init__(self, real, current_target):
        super().__init__(current_target, real)

    def configure(self, src_dir, build_dir):
        # pylint: disable=missing-docstring
        self._call_helper("Configuring", self.real.configure,
                          src_dir, build_dir)

    def build(self, build_dir):
        # pylint: disable=missing-docstring
        self._call_helper("Building", self.real.build,
                          build_dir)

    def install(self, build_dir, path=None):
        # pylint: disable=missing-docstring
        self._call_helper("Installing", self.real.install,
                          build_dir, path)


def build_task(current_target):
    """
    Build a target.

    Arguments
    target - The target to build.
    """

    target = current_target["current_config"]
    build_path = target.get("dp.build_dir")
    if not os.path.exists(build_path):
        os.makedirs(build_path)
    builder = _make_builder(
        current_target,
        lambda r: SimpleBuild(r, current_target))
    builder.configure(target.get("dp.src_dir"), build_path)
    builder.build(build_path)
    if "no_install" not in target:
        builder.install(build_path, path=target.get("install_path",
                                                    "install"))
