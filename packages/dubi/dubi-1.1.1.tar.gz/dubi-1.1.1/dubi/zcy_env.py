import re
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

from env_conf import *
from input_util import get_input
from zcy_service import ZcyService
from zcy_exception import *
from zcy_context import zc


class ZcyEnv:

    def __init__(self, env, host, monitor_url, ak, sk):
        self.env = env
        self.host = host
        self.monitor_url = monitor_url
        self.ak = ak
        self.sk = sk
        self.services = self._retrieve_services()

    def _retrieve_services(self):
        resp = requests.get(self.monitor_url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        service_tr_tags = soup.find_all('tr', id=re.compile('.+'))

        def filter_tag(tr):
            tds = tr.find_all('td')
            return len(tds) >= 5 \
                   and re.match('.+{}[^\.]*$'.format(self.sk), tds[0].string, re.I) \
                   and re.match('.*{}.*'.format(self.ak), tds[1].string, re.I)

        service_tr_tags = filter(filter_tag, service_tr_tags)
        zcy_services = [self._gen_zcy_services(_) for _ in service_tr_tags]
        zcy_services.sort(key=lambda s: s.app + s.name)
        return zcy_services

    def chose_service(self):
        print('Env info [{}]'.format(self.get_info()))
        if len(self.services) == 0:
            print('No service matched!')
        elif len(self.services) == 1:
            print('Only one service matched, chose auto.')
            self._chose_provider_by_context()
        else:
            self._print_services()
            while True:
                try:
                    ins = get_input(self.service_hint(), refresh=self._refresh)
                    index = int(ins[0])
                    if index < 1:
                        raise IndexError
                    zcy_service = self.services[int(ins[0]) - 1]
                    if len(ins) > 1:
                        if ins[1][0] == 'r':
                            zcy_service.chose_provider(True, None)
                        elif ins[1][0] == 'v':
                            zcy_service.chose_provider(False, ins[1][1:])
                        else:
                            zcy_service.chose_provider(False, None)
                    else:
                        zcy_service.chose_provider(False, None)
                    return
                except ValueError:
                    print('Invalid! Input the number of service you chose.')
                except IndexError:
                    print('Index out of range!')
                except ZcyBaseException as e:
                    print(e.msg)

    def _chose_provider_by_context(self):
        service = self.services[0]
        if zc.provider_version is not None:
            service.chose_provider(False, zc.provider_version)
        elif zc.provider_random:
            service.chose_provider(True, None)
        else:
            service.chose_provider(False, None)

    def _refresh(self):
        self.services = self._retrieve_services()
        self._print_services()

    def _gen_zcy_services(self, tr):
        tds = tr.find_all('td')
        name = str(tds[0].string)
        app = str(tds[1].string)
        pro_count = re.sub(r'\D', '', tds[3].a.string)
        pro_count = int(pro_count) if pro_count else 0
        pro_url = self.host + '/' + tds[3].a['href']
        return ZcyService(name, pro_count, pro_url, app)

    def _print_services(self):
        pt = PrettyTable(['No', 'Service', 'Application', 'Provider'])
        pt.align['No'] = 'l'
        pt.align['Service'] = 'l'
        pt.align['Application'] = 'l'
        pt.align['Provider'] = 'l'
        for i, zs in enumerate(self.services):
            pt.add_row([i + 1, zs.name, zs.app, zs.pro_count])
        print(pt)

    @classmethod
    def generate_from(cls, env, ak, sk):
        match_envs = list(filter(lambda x: re.match('.*{}.*'.format(env), x['env'], re.I), env_conf))

        if len(match_envs) == 0:
            raise ZcyNoMatchedEnvException('No matched environment!\nAvailable environments: {}'.format(
                get_available_env()))

        if len(match_envs) > 1:
            raise ZcyAmbiguousEnvException('Ambiguous environment: {}'.format(
                ', '.join(list(map(lambda x: x['env'], match_envs)))))
        else:
            env_name = match_envs[0]['env']
            host = match_envs[0]['url']
            monitor_url = host + '/services.html'
            return ZcyEnv(env_name, host, monitor_url, ak, sk)

    def get_info(self):
        return 'Env: {}, Monitor: {}'.format(self.env, self.monitor_url)

    def service_hint(self):
        return 'Input service number\n' \
               'Append r to chose provider random (like 1 r)\n' \
               'Append v+version to filter providers by version (like 1 v1.0.0)'
