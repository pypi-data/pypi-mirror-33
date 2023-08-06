import pexpect
import telnetlib

from zcy_method import ZcyMethod
from zcy_exception import ZcyNoMethodFoundException


class ZcyProvider:

    def __init__(self, ip, port, service_name, methods, version):
        self.ip = ip
        self.port = port
        self.service_name = service_name
        self.methods = methods
        self.version = version

    def invoke(self, method, parameters):
        if method == 't':
            self.do_telnet()
        else:
            self.do_invoke(method, parameters)

    def do_telnet(self):
        tn = telnetlib.Telnet(self.ip, port=self.port, timeout=20)
        tn.write('\n')
        tn.interact()

    def do_invoke(self, method, parameters):
        if method not in self.methods:
            raise ZcyNoMethodFoundException(
                'Invalid method: {}\nAvailable methods: {}'.format(method, self.methods_to_str()))
        try:
            telnet = pexpect.spawn('telnet {} {}'.format(self.ip, self.port))
            telnet.sendline('\n')
            telnet.expect('dubbo>')

            zcy_method = ZcyMethod(method, parameters)
            invoke_cmd = 'invoke {}.{}'.format(self.service_name, zcy_method.get_invoke_str())
            telnet.sendline(invoke_cmd)
            telnet.expect(' ms.')
            print(telnet.before.decode('GBK') + ' ms.')
        except pexpect.exceptions.TIMEOUT:
            pass

    def get_info(self):
        return 'IP: {}, Port: {}, Methods: {}, Version: {}'.format(self.ip, self.port, self.methods_to_str(), self.version)

    def methods_to_str(self):
        return ', '.join(self.methods)

    def method_hint(self):
        return 'Input method and parameters to invoke\nOr t to entry telnet'
