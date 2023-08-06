#!/usr/bin/python3
"""This module initiates the build."""

import argparse

import devpipeline_core.command

import devpipeline_build.builder


def _list_builders():
    for builder in sorted(devpipeline_build.BUILDERS):
        print("{} - {}".format(builder,
                               devpipeline_build.BUILDERS[builder][1]))


class BuildCommand(devpipeline_core.command.TargetCommand):
    """Class to provide build functionality to dev-pipeline."""

    def __init__(self):
        super().__init__(prog="dev-pipeline build",
                         description="Build targets")
        self.add_argument("--list-builders", action='store_true',
                          default=argparse.SUPPRESS,
                          help="List the available builder tools")
        self.enable_dependency_resolution()
        self.enable_executors()
        self.set_tasks([devpipeline_build.builder.build_task])
        self.helper_fn = lambda: super(BuildCommand, self).process()

    def setup(self, arguments):
        if "list_builders" in arguments:
            self.helper_fn = _list_builders

    def process(self):
        self.helper_fn()


def main(args=None):
    # pylint: disable=missing-docstring
    builder = BuildCommand()
    # pylint: disable=missing-docstring
    devpipeline_core.command.execute_command(builder, args)


_BUILD_COMMAND = (main, "Build and install a set of components.")

if __name__ == '__main__':
    main()
