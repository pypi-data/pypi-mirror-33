#!/usr/bin/python3
"""This modules generates a build ordered list of targets."""

import argparse

import devpipeline_core.config.config
import devpipeline_core.command
import devpipeline_core.plugin
import devpipeline_core.resolve


_ORDER_OUTPUTS = devpipeline_core.plugin.query_plugins(
    'devpipeline.build_order.methods')


def _list_methods(targets, components):
    # neither argument is required
    del targets
    del components

    for key in sorted(_ORDER_OUTPUTS):
        print("{} - {}".format(key, _ORDER_OUTPUTS[key][1]))


class BuildOrderer(devpipeline_core.command.TargetCommand):

    """This class outputs an ordered list of the packages to satisfy dependencies."""

    def __init__(self):
        super().__init__(prog="dev-pipeline build-order",
                         description="Determinte all dependencies of a set of "
                                     "targets and the order they should be "
                                     "built in.")
        self.add_argument("--method",
                          help="The method used to display build order.",
                          default="list")
        self.add_argument("--list-methods", action='store_true',
                          default=argparse.SUPPRESS,
                          help="List the available methods instead of printing"
                               " dependency information.")
        self.helper_fn = None

    def setup(self, arguments):
        if "list_methods" in arguments:
            self.helper_fn = _list_methods
        else:
            build_order = _ORDER_OUTPUTS.get(arguments.method)
            if not build_order:
                raise Exception("Invalid method: {}".format(arguments.method))
            self.helper_fn = build_order[0]

    def process(self):
        self.helper_fn(self.targets, self.components)


def main(args=None):
    # pylint: disable=missing-docstring
    build_orderer = BuildOrderer()
    devpipeline_core.command.execute_command(build_orderer, args)


_BUILD_ORDER_COMMAND = (
    main, "Generate dependency information about project components.")

if __name__ == '__main__':
    main()
