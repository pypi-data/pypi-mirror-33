"""
Some plugins to support the tests.
"""

from __future__ import print_function

import random

import caparg as ca
import elcaminoreal


COMMANDS = elcaminoreal.Commands()


@COMMANDS.dependency(name="foo", dependencies=["bar"])
def a_foo(dependencies, _possible_dependencies):
    """
    Depend on a bar object
    """
    return dict(bar=dependencies['bar'])


@COMMANDS.dependency(dependencies=["bar", "quux"],
                     possible_dependencies=["foo"],
                     regular=True)
def regular(bar, quux, build_foo):
    """
    Depend on bar, maybe on foo

    Use regular arguments.
    """
    return dict(bar=bar, quux=quux, foo=build_foo())


@COMMANDS.dependency(possible_dependencies=["bar"])
def foo_2(_dependencies, possible_dependencies):
    """
    Depend on a bar object in an optional way.
    """
    return dict(bar=possible_dependencies['bar']())


@COMMANDS.dependency(name="bar")
def a_bar(_dependencies, _possible_dependencies):
    """
    Return a bar-like object.
    """
    return "I'm a bar"


@COMMANDS.dependency(name="quux")
def a_quux(_dependencies, _possible_dependencies):
    """
    Return a quux-like object.
    """
    return "I'm a quux"


@COMMANDS.dependency()
def rand(_dependencies, _possible_dependencies):
    """
    Generate a random number.
    """
    return random.random()


@COMMANDS.dependency(dependencies=["rand"])
def needs_rand(dependencies, _possible_dependencies):
    """
    Depend on a random number.
    """
    return dict(rand=dependencies["rand"])


@COMMANDS.dependency(name="baz")
def a_baz(dependencies, _possible_dependencies):
    """
    Use an undeclared dependency.
    """
    return dependencies['bar']


@COMMANDS.dependency(dependencies=['tuck'])
def robin(_dependencies, _possible_dependencies):
    """
    Depend on tuck
    """


@COMMANDS.dependency(dependencies=['robin'])
def tuck(_dependencies, _possible_dependencies):
    """
    Depend on robin
    """


@COMMANDS.dependency(name='print')
def _print(_dependencies, _possible_dependencies):
    """
    Return a function to display things on the terminal.
    """
    return print


@COMMANDS.dependency(name='output')
def dummy_output(_dependencies, _possible_dependencies):
    """
    Literally do nothing.

    This is designed for being overridden.
    """


@COMMANDS.command(dependencies=['foo', 'output'],
                  parser=ca.command('',
                                    ca.positional('lili', type=str)),
                  regular=True)
def regular_command(foo, lili, output):
    """
    Use regular arguments

    Output results
    """
    output(foo, lili)


@COMMANDS.command(dependencies=['foo', 'print'],
                  parser=ca.command('',
                                    ca.positional('lala', type=str)))
def show(args, dependencies):
    """
    Print then arguments.
    """
    dependencies['print'](args, "BREAK", dependencies)


@COMMANDS.command(dependencies=['bar', 'print'],
                  parser=ca.command('',
                                    wooo=ca.option(type=str)))
def gowoo(args, dependencies):
    """
    Print 'woo' and then arguments.
    """
    dependencies['print']("woo", args, dependencies)


@COMMANDS.command(dependencies=['print'],
                  parser=ca.command('',
                                    foo=ca.option(type=str),
                                    bar=ca.option(type=str, required=True)))
def interesting_args(args, dependencies):
    """
    Print arguments.
    """
    dependencies['print'](args.get('foo'), args['bar'])
