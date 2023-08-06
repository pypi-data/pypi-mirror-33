import re
import random
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

from input_util import get_input
from zcy_provider import ZcyProvider
from zcy_exception import *
from zcy_context import zc


class ZcyService:

    pvk = None

    def __init__(self, name, pro_count, pro_url, app):
        self.name = name
        self.pro_count = pro_count
        self.pro_url = pro_url
        self.app = app
        self.providers = None

    def retrieve_providers(self, version=None):
        resp = requests.get(self.pro_url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        provider_tags = soup.find_all('td', id=re.compile(r'.*_0$'))

        if version is not None:
            p = '.*version=.*{}.*'.format(version)
            provider_tags = filter(lambda x: re.match(p, x.string), provider_tags)

        zcy_providers = [self._gen_zcy_provider(_.string.encode()) for _ in provider_tags]
        zcy_providers = list(filter(lambda x: x is not None, zcy_providers))
        zcy_providers.sort(key=lambda p: p.ip)
        return zcy_providers

    def chose_provider(self, is_random, version):
        print('Service info: [{}]'.format(self.get_info()))
        self.providers = self.retrieve_providers(version)
        self._print_providers()
        if len(self.providers) == 1:
            print('Only one provider matched, chose auto.')
            self._chose_index(0)
        elif is_random:
            self._chose_random()
        elif version:
            self._chose_version(version)
        else:
            self._chose_manual()

    def _chose_random(self):
        index = random.randint(0, len(self.providers) - 1)
        print('Random chose index {}'.format(index + 1))
        self._chose_index(index)

    def _chose_version(self, version):
        providers = list(filter(lambda x: x.version == version, self.providers))
        if len(providers) == 0:
            distinct_versions = set(map(lambda x: x.version, self.providers))
            raise ZcyNoProviderVersionFoundException('No provider version {} found! \nAvailable version: {}'
                                                     .format(version, ', '.join(distinct_versions)))
        index = 0
        self._chose_index(index)

    def _chose_manual(self):
        try:
            ins = get_input(self.provider_hint(), refresh=self._refresh)
            index = int(ins[0])
            if index < 1:
                raise IndexError

            self._chose_index(index - 1)
        except ValueError:
            print('Invalid! Input the number of provider you chose.')
        except IndexError:
            print('Index out of range!')

    def _chose_index(self, index):
        provider = self.providers[index]
        print('Provider info [{}]'.format(provider.get_info()))
        if zc.telnet:
            provider.do_telnet()
        elif zc.method is not None:
            provider.do_invoke(zc.method, zc.signature)
        else:
            self._invoke_provider(provider)

    def _refresh(self):
        self.providers = self.retrieve_providers()
        self._print_providers()

    def _get_signatures(self, provider):
        signatures = get_input(provider.method_hint())
        if len(signatures) < 1:
            return self._get_signatures()
        if len(signatures) >= 2:
            return signatures[0:2]
        else:
            return [signatures[0], None]

    def _invoke_provider(self, provider):
        try:
            signatures = self._get_signatures(provider)
            provider.invoke(*signatures)
        except ZcyBaseException as e:
            print(e.msg)
            self._invoke_provider(provider)

    def _gen_zcy_provider(self, string):
        match = re.search(r'dubbo://([\d\.]*):(\d{1,5})/.*methods=([^&]*).*version=(.*)$', string)
        if match is None:
            return None
        ip = match.group(1)
        port = match.group(2)
        service_name = self.name
        methods = match.group(3).split(',')
        methods.sort(key=lambda x: x)
        version = match.group(4)
        return ZcyProvider(ip, port, service_name, methods, version)

    def _print_providers(self):
        pt = PrettyTable(['No', 'IP', 'Port', 'Methods', 'Version'])
        pt.align['No'] = 'l'
        pt.align['IP'] = 'l'
        pt.align['Port'] = 'l'
        pt.align['Methods'] = 'l'
        pt.align['Version'] = 'l'
        for i, zp in enumerate(self.providers):
            pt.add_row([i + 1, zp.ip, zp.port, zp.methods_to_str(), zp.version])
        print(pt)

    def get_info(self):
        return 'Name: {}, Application: {}'.format(self.name, self.app)

    def provider_hint(self):
        return 'Chose the provider'
