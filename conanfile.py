from conans import ConanFile, tools
import os
import platform


class XmlrpccConan(ConanFile):
    name = 'xmlrpc-c'
    version = '1.39.12'
    license = 'MIT'
    url = 'https://github.com/sztomi/xmlrpc-c-conan'
    settings = 'os', 'compiler', 'build_type', 'arch'
    tarball_url = 'https://sourceforge.net/projects/xmlrpc-c/files/Xmlrpc-c%20Super%20Stable/1.39.12/xmlrpc-c-{}.tgz'.format(version)
    dirname = 'xmlrpc-c-{}'.format(version)
    requires = ('libcurl/7.50.3@sztomi/stable')
    default_options = ('libcurl:shared=False')

    def source(self):
        tarball_name = 'xmlrpc-c-{}.tgz'.format(self.version)
        tools.download(self.tarball_url, tarball_name)
        tools.untargz(tarball_name)

    def build(self):
        os.chdir(self.dirname)
        curl_config = '"{}/curl-config"'.format(self.deps_cpp_info['libcurl'].bin_paths[0])
        self.run('chmod +x {}'.format(curl_config))
        self.run('CPPFLAGS=-I{} LDFLAGS=-L{} CURL_CONFIG={} bash -c "./configure --enable-curl-client"'.format(
            self.deps_cpp_info['libcurl'].include_paths[0],
            self.deps_cpp_info['libcurl'].lib_paths[0],
            curl_config))
        # without this, the makefile won't find the curl-config from the libcurl pkg
        tools.replace_in_file('lib/curl_transport/Makefile', 'shell curl-config', 'shell ' + curl_config)
        self.run('make')

    def package(self):
        # plenty of symlink loops prevent copying on Linux
        if platform.system() == 'Linux':
            build_dir = os.path.abspath('{}/../../build'.format(self.package_folder))
            self.run('find {} -xtype l -delete'.format(build_dir))
            self.run('find {} -name "{}" -delete'.format(build_dir, 'blddir'))
            self.run('find {} -name "{}" -delete'.format(build_dir, 'srcdir'))
        self.copy('*.h', src='{}/{}'.format(self.dirname, 'include'), dst='include')
        self.copy('*.hpp', src='{}/{}'.format(self.dirname, 'include'), dst='include')
        self.copy('*.so', dst='lib', keep_path=False)
        self.copy('*.dll', dst='lib', keep_path=False)
        self.copy('*.lib', dst='lib', keep_path=False)
        self.copy('*.a', dst='lib', keep_path=False)

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

