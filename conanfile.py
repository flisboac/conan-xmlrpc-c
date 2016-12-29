from conans import ConanFile, tools
import os


class XmlrcpcConan(ConanFile):
    name = 'xmlrcp-c'
    version = '1.39.12'
    license = 'MIT'
    url = 'https://github.com/sztomi/xmlrpc-c-conan'
    settings = 'os', 'compiler', 'build_type', 'arch'
    tarball_url = 'https://sourceforge.net/projects/xmlrpc-c/files/Xmlrpc-c%20Super%20Stable/1.39.12/xmlrpc-c-{}.tgz'.format(version)
    dirname = 'xmlrpc-c-{}'.format(version)

    def source(self):
        tarball_name = 'xmlrpc-c-{}.tgz'.format(self.version)
        tools.download(self.tarball_url, tarball_name)
        tools.untargz(tarball_name)

    def build(self):
        os.chdir(self.dirname)
        self.run('./configure --prefix={}'.format(self.package_folder))
        self.run('make')
        self.run('make install')

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = [
            'xmlrpc_server_cgi++',
            'xmlrpc_server_abyss++',
            'xmlrpc_util++',
            'xmlrpc_packetsocket',
            'xmlrpc_server_pstream++',
            'xmlrpc',
            'xmlrpc_server++',
            'xmlrpc_server_abyss',
            'xmlrpc_server_cgi',
            'xmlrpc_xmlparse',
            'xmlrpc_server',
            'xmlrpc_abyss++',
            'xmlrpc_abyss',
            'xmlrpc_xmltok',
            'xmlrpc++',
            'xmlrpc_client',
            'xmlrpc_client++',
            'xmlrpc_util',
            'xmlrpc_cpp'
        ]
