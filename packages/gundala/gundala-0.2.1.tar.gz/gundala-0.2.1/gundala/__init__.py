import argparse
import socket
import ssl
import struct
import asyncore
import random
import string
from .templates import contact, domain
from bs4 import BeautifulSoup

class EPP(asyncore.dispatcher):

    def __init__(self, **kwargs):
        asyncore.dispatcher.__init__(self)
        self.config = kwargs
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)
        self.socket.connect((self.config['host'], self.config['port']))
        self.cert = self.config['cert'] if 'cert' in self.config else None
        try:
            context = ssl.SSLContext(
                getattr(ssl, 'PROTOCOL_TLS_CLIENT', ssl.PROTOCOL_SSLv23))
            if self.cert:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.load_cert_chain(self.cert)

            self.ssl = context.wrap_socket(
                self.socket, server_hostname=self.config['host'])
        except Exception as err:
            print(err)
            print("ERROR: Could not setup a secure connection.")
            print("Check whether your IP is allowed to connect to the host.")
            exit(1)
        self.format_32 = self.format_32()
        self.login()
        asyncore.loop()

    def __del__(self):
        try:
            self.logout()
            self.socket.close()
        except TypeError:
            """ Will occur when not properly connected """
            pass

    # http://www.bortzmeyer.org/4934.html

    def format_32(self):
        # Get the size of C integers. We need 32 bits unsigned.
        format_32 = ">I"
        if struct.calcsize(format_32) < 4:
            format_32 = ">L"
            if struct.calcsize(format_32) != 4:
                raise Exception("Cannot find a 32 bits integer")
        elif struct.calcsize(format_32) > 4:
            format_32 = ">H"
            if struct.calcsize(format_32) != 4:
                raise Exception("Cannot find a 32 bits integer")
        else:
            pass
        return format_32

    def int_from_net(self, data):
        return struct.unpack(self.format_32, data)[0]

    def int_to_net(self, value):
        return struct.pack(self.format_32, value)

    def cmd(self, cmd, silent=False):
        self.write(cmd.encode('utf-8'))
        soup = BeautifulSoup(self.read(), 'lxml')
        response = soup.find('response')
        result = soup.find('result')
        try:
            code = int(result.get('code'))
        except AttributeError:
            print("\nERROR: Could not get result code, exiting.")
            exit(1)
        if not silent or code not in (1000, 1300, 1500):
            print("- [%d] %s" % (code, result.msg.text))
        if code == 2308:
            return False
        if code == 2502:
            return False
        # try:
        #     code = int(result.get('code'))
        # except Exception as err:
        #     print(err)
        return response

    def read(self):
        length = self.ssl.read(4)
        if length:
            i = self.int_from_net(length)-4
            return self.ssl.read(i)

    def write(self, xml):
        epp_as_string = xml
        # +4 for the length field itself (section 4 mandates that)
        # +2 for the CRLF at the end
        length = self.int_to_net(len(epp_as_string) + 4 + 2)
        self.ssl.send(length)
        return self.ssl.send(epp_as_string + b"\r\n")

    def login(self):
        """ Read greeting """
        greeting = self.read()
        soup = BeautifulSoup(greeting, 'lxml')
        svid = soup.find('svid')
        version = soup.find('version')
        print("Connected to %s (v%s)\n" % (svid.text, version.text))

        """ Login """
        xml = domain.login % self.config
        if not self.cmd(xml, silent=True):
            exit(1)

    def logout(self):
        cmd = domain.logout
        return self.cmd(cmd, silent=True)

    def poll(self):
        cmd = domain.poll
        return self.cmd(cmd)


class EPPObject(asyncore.dispatcher):
    def __init__(self, epp):
        asyncore.dispatcher.__init__(self)
        self.epp = epp

    def __str__(self):
        return str(self).encode('utf-8')

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            pass


class Contact(EPPObject):
    def __init__(self, epp, handle=False, **kwargs):
        self.epp = epp
        self.handle = handle
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        try:
            self.name != ''
            return "[%(handle)s] %(name)s, %(street)s, %(pc)s %(city)s (%(cc)s)" % self
        except:
            return self.handle

    def available(self):
        try:
            cmd = contact.available % self
            res = self.epp.cmd(cmd, silent=True)
            return res.resdata.find('contact:id').get('avail') == 'true'
        except Exception as e:
            print('Failed to get contact availability.')

    def create(self):
        try:
            cmd = contact.create % self
            res = self.epp.cmd(cmd).resdata
            return res.find('contact:id').text
        except Exception as e:
            print('Failed to create contact.')

    def info(self):
        try:
            cmd = contact.info % self
            res = self.epp.cmd(cmd).resdata

            self.roid = res.find('contact:roid').text
            self.status = res.find('contact:status').get('s')
            self.name = res.find('contact:name').text
            try:
                self.street = res.find('contact:street').text
            except AttributeError:
                pass
            self.city = res.find('contact:city').text
            try:
                self.pc = res.find('contact:pc').text
            except AttributeError:
                pass
            self.cc = res.find('contact:cc').text
            self.voice = res.find('contact:voice').text
            self.email = res.find('contact:email').text
            return self
        except Exception as e:
            print('Failed to get info.')

    def update(self):
        try:
            cmd = contact.update % self
            return self.epp.cmd(cmd)
        except Exception as e:
            print('Failed to update contact.')


class Domain(EPPObject):
    def __init__(self, epp, domain):
        self.domain = domain
        self.epp = epp
        self.roid = ""
        self.status = ""
        #self.ns = Nameserver(epp)

    def __unicode__(self):
        return "[%(domain)s] status: %(status)s, registrant: %(registrant)s, admin: %(admin)s, tech: %(tech)s" % self

    def available(self):
        try:
            cmd = domain.available % self.domain
            res = self.epp.cmd(cmd)
            return res.resdata.find('domain:name').get('avail') == '1'
        except Exception as e:
            print('Failed to check domain availability.')

    def create(self, contacts, ns, period=1, eppcode=None):
        try:
            if not eppcode:
                eppcode = ''.join(random.choice(string.ascii_uppercase +
                                          string.ascii_lowercase +
                                          string.digits +
                                          '!@#$%^&*()') for _ in range(10))

            cmd = domain.create % dict({
                'domain': self.domain,
                'ns': ns[0],
                'registrant': contacts['registrant'],
                'admin': contacts['admin'],
                'tech': contacts['tech'],
                'eppcode': eppcode,
                'regperiod': period
            })
            res = self.epp.cmd(cmd)
        except Exception as e:
            print('Failed to register domain.')

    def delete(self, undo=False):
        try:
            if undo:
                cmd = domain.canceldelete % self.domain
            else:
                cmd = domain.delete % self.domain
            return self.epp.cmd(cmd)
        except Exception as e:
            print('Failed to unregister domain.')

    def info(self):
        try:
            cmd = domain.info % self.domain
            res = self.epp.cmd(cmd).resdata
            self.roid = res.find('domain:roid').text
            self.status = res.find('domain:status').get('s')
            self.registrant = Contact(
                self.epp, res.find('domain:registrant').text)
            self.admin = Contact(self.epp, res.find(
                'domain:contact', type='admin').text)
            self.tech = Contact(self.epp, res.find(
                'domain:contact', type='tech').text)
            return self
        except Exception as e:
            print('Failed to get domain info.')

    def token(self):
        try:
            cmd = domain.info % self.domain
            res = self.epp.cmd(cmd)
            return res.resdata.find('domain:pw').text
        except Exception as e:
            print('Failed to get token.')

    def transfer(self, token):
        try:
            cmd = domain.transfer % dict({
                'domain': self.domain,
                'token': token,
            })
            return self.epp.cmd(cmd)
        except Exception as e:
            print('Failed to transfer domain.')


class Nameserver(EPPObject):
    def __init__(self, epp, nameserver=False):
        self.nameserver = nameserver
        self.epp = epp

    def __unicode__(self):
        return self.nameserver

    def get_ip(self):
        try:
            cmd = domain.nameserver % self.nameserver
            res = self.epp.cmd(cmd)
            return res.resdata.find('host:addr').text
        except Exception as e:
            print('Failed to get ip address.')
