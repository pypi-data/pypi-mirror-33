"""
Test dependencies and commands
"""
from __future__ import print_function

import unittest

import six

import elcaminoreal
from elcaminoreal.test import some_plugins


class DependencyResolverTester(unittest.TestCase):

    """
    Dependency resolution tests
    """

    def test_mkgraph(self):
        """
        mkgraph finds and runs dependencies without subdependencis
        """
        result = some_plugins.COMMANDS.mkgraph(['bar'])
        self.assertEquals(result.pop('bar'), "I'm a bar")
        self.assertEquals(result, {})

    def test_mkgraph_cycle(self):
        """
        mkgraph raises ValueError when it detects a cycle
        """
        with self.assertRaises(ValueError):
            some_plugins.COMMANDS.mkgraph(['robin'])

    def test_mkgraph_random(self):
        """
        mkgraph caches subdependencies
        """
        result = some_plugins.COMMANDS.mkgraph(['rand', 'needs_rand'])
        self.assertEquals(result['rand'], result['needs_rand']['rand'])

    def test_mkgraph_possible(self):
        """
        mkgraph possible dependencies are functions that return the object
        """
        result = some_plugins.COMMANDS.mkgraph(['foo_2'])
        self.assertEquals(result['foo_2'], dict(bar="I'm a bar"))

    def test_mkgraph_regular(self):
        """
        mkgraph regular functions work
        """
        result = some_plugins.COMMANDS.mkgraph(['regular'])
        self.assertEquals(result['regular']['bar'], result['bar'])
        self.assertEquals(result['regular']['quux'], result['quux'])
        self.assertEquals(result['regular']['foo'], result['foo'])


class RunnerResolverTester(unittest.TestCase):

    """
    Command running tests
    """

    def test_run(self):
        """
        Run calls the command with the dependencies it requested
        """
        output = []

        def _my_print(*args):
            output.append(' '.join(map(str, args)))
        some_plugins.COMMANDS.run(['show', 'heee'],
                                  override_dependencies=dict(print=_my_print))
        self.assertEquals(len(output), 1)
        args, deps = output[0].split('BREAK', 1)
        self.assertIn('hee', args)
        self.assertIn('foo', deps)
        self.assertIn('bar', deps)

    def test_args(self):
        """
        Argument parsing respects required/not-required
        """
        output = []

        def _my_print(*args):
            output.append(' '.join(map(str, args)))
        some_plugins.COMMANDS.run(['interesting-args', '--bar', 'ddd'],
                                  override_dependencies=dict(print=_my_print))
        self.assertEquals(len(output), 1)
        my_foo, my_bar = output.pop().split(' ')
        self.assertEquals(my_foo, 'None')
        self.assertEquals(my_bar, 'ddd')

    def test_required(self):
        """
        Argument parsing without required arguments fails`
        """
        with self.assertRaises(BaseException):
            some_plugins.COMMANDS.run(['interesting_args', '--foo', 'ddd'])

    def test_error_redirect(self):
        """
        Error redirect sends error message to file pointer
        """
        filep = six.moves.StringIO('w')
        with elcaminoreal.errors_to(filep):
            some_plugins.COMMANDS.run(['no-such-command'])
        error_message = filep.getvalue().splitlines()
        self.assertEquals(error_message.pop(0), 'Usage:')

    def test_regular(self):
        """
        Asking for regular arguments calls functions with argument names
        """
        output = []

        def _my_output(*args):
            output.append(args)
        dependencies = dict(output=_my_output)
        some_plugins.COMMANDS.run(['regular-command', 'thing'],
                                  override_dependencies=dependencies)
        self.assertEquals(len(output), 1)
        self.assertEquals(output[0][0]['bar'], "I'm a bar")
        self.assertEquals(output[0][1], 'thing')
