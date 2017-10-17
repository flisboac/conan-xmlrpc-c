from conans import ConanFile, tools
import os
import platform

deps = (
    ('libcurl', '7.50.3', 'lasote', 'stable'),
)

CONAN_PACKAGE_USER = os.getenv('CONAN_USER', '') or 'flisboac'
CONAN_PACKAGE_CHANNEL = os.getenv('CONAN_CHANNEL', '') or 'testing'

class ConanPackage(ConanFile):

    short_paths = True
    name = 'xmlrpc-c'
    distname = 'conan-{}'.format(name)
    version = '1.39.12'
    license = 'MIT'
    user = os.getenv('CONAN_USER', '') or 'flisboac'
    channel = os.getenv('CONAN_CHANNEL', '') or 'testing'
    url = 'https://github.com/{}/{}'.format(user, distname)
    tarball_url = (os.getenv('CONAN_SOURCE_URL', '') or 
        'https://sourceforge.net/projects/xmlrpc-c/files/Xmlrpc-c%20Super%20Stable/{}/xmlrpc-c-{}.tgz'.format(version, version))
    fullname = '{}/{}@{}/{}'.format(name, version, user, channel)
    dirname = 'xmlrpc-c-{}'.format(version)
    requires = tuple( '{}/{}@{}/{}'.format(dep[0], dep[1], (dep[2:]+(CONAN_PACKAGE_USER,))[0], (dep[3:]+(CONAN_PACKAGE_CHANNEL,))[0])
        for dep in deps)
    default_options = ('libcurl:shared=False')

    def source(self):
        tarball_name = 'xmlrpc-c-{}.tgz'.format(self.version)
        tools.download(self.tarball_url, tarball_name)
        tools.untargz(tarball_name)

    def as_unix_path(self, path, *paths):
        if platform.system() == 'Windows':
            all_paths = [tools.unix_path(path)]
            all_paths.extend(tools.unix_path(p) for p in paths)
        else:
            all_paths = [path]
            all_paths.extend(paths)
        return '/'.join(all_paths)

    def non_windows_run(self, command):
        if platform.system() != 'Windows':
            return self.run(command)

    def windows_aware_run(self, command):
        if platform.system() == 'Windows':
            return tools.run_in_windows_bash(self, command)
        else:
            return self.run(command)

    def build(self):
        os.chdir(self.dirname)

        # Calculating correct pathnames
        bin_paths = tuple(self.as_unix_path(self.deps_cpp_info['libcurl'].rootpath, dir) for dir in self.deps_cpp_info['libcurl'].bindirs)
        include_paths = tuple(self.as_unix_path(self.deps_cpp_info['libcurl'].rootpath, dir) for dir in self.deps_cpp_info['libcurl'].includedirs)
        lib_paths = tuple(self.as_unix_path(self.deps_cpp_info['libcurl'].rootpath, dir) for dir in self.deps_cpp_info['libcurl'].libdirs)
        curl_config = '"{}"'.format(self.as_unix_path(bin_paths[0], 'curl-config'))

        # Making sure curl_config is executable
        self.non_windows_run('chmod +x {}'.format(curl_config))

        # Configuring
        self.windows_aware_run('CPPFLAGS=-I{} LDFLAGS=-L{} CURL_CONFIG={} bash -c "./configure --enable-curl-client"'.format(
            include_paths[0], lib_paths[0], curl_config)
        )

        # without this, the makefile won't find the curl-config from the libcurl pkg
        tools.replace_in_file('lib/curl_transport/Makefile', 'shell curl-config', 'shell ' + curl_config)

        fs_linker = ''
        if platform.system() == 'Windows':
            fs_linker = 'LN_S="cp -r"'
        self.windows_aware_run('make {}'.format(fs_linker))

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

