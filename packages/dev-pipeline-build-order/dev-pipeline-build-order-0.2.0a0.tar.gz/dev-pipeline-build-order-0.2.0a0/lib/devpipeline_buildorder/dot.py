#!/usr/bin/python3

"""
Output methods that use dot syntax to represent dependency information.
"""

import re
import sys

import devpipeline_core.resolve


def _dotify(string):
    """This function swaps '-' for '_'."""
    return re.sub("-", lambda m: "_", string)


def _do_dot(targets, components, layer_fn):
    def _handle_layer_dependencies(resolved_dependencies, attributes):
        for component in resolved_dependencies:
            stripped_name = _dotify(component)
            component_dependencies = components[component].get("depends")
            if component_dependencies:
                for dep in devpipeline_core.config.config.split_list(
                        component_dependencies):
                    print("{} -> {} {}".format(stripped_name,
                                               _dotify(dep), attributes))
            print("{} {}".format(stripped_name, attributes))

    print("digraph dependencies {")
    try:
        devpipeline_core.resolve.process_dependencies(
            targets, components, lambda rd: layer_fn(
                rd, lambda rd: _handle_layer_dependencies(
                    rd, "")))
    except devpipeline_core.resolve.CircularDependencyException as cde:
        layer_fn(
            cde.components,
            lambda rd: _handle_layer_dependencies(
                rd, "[color=\"red\"]"))
    print("}")


def _print_layers(targets, components):
    """
    Print dependency information, grouping components based on their position
    in the dependency graph.  Components with no dependnecies will be in layer
    0, components that only depend on layer 0 will be in layer 1, and so on.

    If there's a circular dependency, those nodes and their dependencies will
    be colored red.

    Arguments
    targets - the targets explicitly requested
    components - full configuration for all components in a project
    """
    layer = 0

    def _add_layer(resolved_dependencies, dep_fn):
        nonlocal layer

        print("subgraph cluster_{} {{".format(layer))
        print("label=\"Layer {}\"".format(layer))
        dep_fn(resolved_dependencies)
        print("}")
        layer += 1

    _do_dot(targets, components, _add_layer)


_LAYERS_TOOL = (
    _print_layers,
    "Print a dot graph that groups components by their position in a layered "
    "architecture.  Components are only permitted to depend on layers with a "
    "lower number.")


def _print_graph(targets, components):
    """
    Print dependency information using a dot directed graph.  The graph will
    contain explicitly requested targets plus any dependencies.

    If there's a circular dependency, those nodes and their dependencies will
    be colored red.

    Arguments
    targets - the targets explicitly requested
    components - full configuration for all components in a project
    """
    _do_dot(targets, components, lambda rd, dep_fn: dep_fn(rd))


_GRAPH_TOOL = (
    _print_graph,
    "Print a dot graph where each component points at its dependnet "
    "components.")


def _print_dot(targets, components):
    """
    Deprecated function; use print_graph.

    Arguments
    targets - the targets explicitly requested
    components - full configuration for all components in a project
    """
    print("Warning: dot option is deprecated.  Use graph instead.",
          file=sys.stderr)
    _print_graph(targets, components)


_DOT_TOOL = (_print_dot, "Deprecated -- use the \"graph\" option instead.")
