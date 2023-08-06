import argparse

from info import *
from zcy_action import *

parser = argparse.ArgumentParser(prog='dubi', description=description,
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog='Source: {}\nContact Me: {}'.format(source, email))

p_group = parser.add_mutually_exclusive_group()
i_group = parser.add_mutually_exclusive_group()

parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(version))

parser.add_argument('-e', '--env', nargs=0, action=ShowEnvAction, help='show the available environment and exit')

parser.add_argument('arg', nargs='+', action=EnvAction, help='env [app] [service] (ignore case match)')

p_group.add_argument('-pv', '--provider_version', nargs=1, action=ProviderVersionAction,
                    help='specify the version of provider if only one service matched (e.g., -pv 1.0.0)')
p_group.add_argument('-pr', '--provider_random', nargs=0, action=ProviderRandomAction,
                    help='chose provider random if only one service matched')

i_group.add_argument('-t', '--telnet', nargs=0, action=DoTelnetAction,
                    help='telnet provider if only one provider matched')
i_group.add_argument('-i', '--invoke', nargs=2, action=InvokeAction,
                    help='invoke the provider with method info given if only one provider matched (e.g., -i fun ())')

