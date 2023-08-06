from argparse import Action

from env_conf import get_available_env
from zcy_env import ZcyEnv
from zcy_service import ZcyService
from zcy_exception import ZcyBaseException
from zcy_context import zc


class ShowEnvAction(Action):

    def __call__(self, *args, **kwargs):
        print('Available environment: {}'.format(get_available_env()))


class ProviderVersionAction(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        zc.provider_version = values[0]


class ProviderRandomAction(Action):

    def __call__(self, *args, **kwargs):
        zc.provider_random = True


class DoTelnetAction(Action):

    def __call__(self, *args, **kwargs):
        zc.telnet = True


class InvokeAction(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        zc.method = values[0]
        zc.signature = values[1] if values[1] != '.' else ''


class EnvAction(Action):

    def __call__(self, parser, namespace, values, option_string=None):

        def get_par(index):
            try:
                return values[index]
            except IndexError:
                return None

        env = values[0]
        ak = get_par(1) or '.'
        sk = get_par(2) or '.'
        ZcyService.pvk = get_par(3) or None

        try:
            zcy_env = ZcyEnv.generate_from(env, ak, sk)
            zcy_env.chose_service()
        except ZcyBaseException as e:
            print(e.msg)
