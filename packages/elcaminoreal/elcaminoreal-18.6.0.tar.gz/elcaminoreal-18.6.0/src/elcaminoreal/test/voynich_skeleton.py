"""
Skeleton for Voynich

Voynich is a system for encrypting secrets.
This is a rough skeleton, to show-case how elcaminoreal
would work for a real command.
"""
import os
import sys

import caparg as ca
import elcaminoreal

COMMANDS = elcaminoreal.Commands()


@COMMANDS.dependency()
def current_directory(_deps, _maybedeps):
    """
    Current working directory
    """
    return '.'


@COMMANDS.dependency()
def environment(_deps, _maybedeps):
    """
    Environment dictionary
    """
    return os.environ


@COMMANDS.dependency(dependencies=['environment', 'current_directory'])
def secret_filename(dependencies, _maybedeps):
    """
    The filename to put the encrypted secrets in.
    """
    if 'VOYNICH_FILE' in dependencies['environment']:
        return dependencies['environment']['VOYNICH_FILE']
    return os.path.join(dependencies['current_directory'], 'voynich.json')


@COMMANDS.command(dependencies=['secret_filename'],
                  parser=ca.command('',
                                    key_file=ca.option(type=str,
                                                       required=True)))
def create(args, dependencies):
    """
    Create a new secrets file (and save the private key).
    """
    sys.stdout.write("writing key to {} and public data to {}\n".format(
        args.key_file,
        dependencies['secret_filename']))


@COMMANDS.command(dependencies=['secret_filename'],
                  parser=ca.command('',
                                    name=ca.option(type=str, required=True),
                                    value=ca.option(type=str, required=True)))
def encrypt(args, dependencies):
    """
    Add a new encrypted secret to the dependencies.
    """
    sys.stdout.write("adding to {} name {} value {}\n".format(
        dependencies['secret_filename'],
        args.name,
        args.value))


@COMMANDS.command(dependencies=['secret_filename'],
                  parser=ca.command('',
                                    key_file=ca.option(type=str,
                                                       required=True),
                                    directory=ca.option(type=str,
                                                        required=True)))
def decrypt(args, dependencies):
    """
    Decrypt the secrets from a file into a directory
    """
    sys.stdout.write("decrypting {} using {} into {}\n".format(
        dependencies['secret_filename'],
        args.key_file,
        args.directory))
