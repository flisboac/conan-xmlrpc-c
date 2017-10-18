from conans import ConanFile, tools
import os
import platform

deps = (
    { 'name': 'libcurl', 'version': '7.50.3', 'user': 'lasote', 'channel': 'stable' },
)

CONAN_PACKAGE_USER = os.getenv('CONAN_USER', '') or 'flisboac'
CONAN_PACKAGE_CHANNEL = os.getenv('CONAN_CHANNEL', '') or 'testing'


def to_full_package_name(dep):
    return '{}/{}@{}/{}'.format(
        dep['name'], 
        dep['version'], 
        dep.get('user', CONAN_PACKAGE_USER), 
        dep.get('channel', CONAN_PACKAGE_CHANNEL)
    )

def get_dep(name):
    for dep in deps:
        if dep['name'] == name: return dep

class ConanPackageBase(ConanFile):

    short_paths = True
    build_policy = "missing"
    settings = "os", "compiler", "build_type", "arch"

    name = 'xmlrpc-c'
    description = 'A lightweight RPC library based on XML and HTTP.'
    distname = 'conan-{}'.format(name)
    version = '1.39.12'
    license = 'MIT'
    user = os.getenv('CONAN_USER', '') or 'flisboac'
    channel = os.getenv('CONAN_CHANNEL', '') or 'testing'
    url = 'https://github.com/{}/{}'.format(user, distname)
    tarball_url = (os.getenv('CONAN_SOURCE_URL', '') or 
        'https://sourceforge.net/projects/xmlrpc-c/files/Xmlrpc-c%20Super%20Stable/{}/xmlrpc-c-{}.tgz'.format(version, version))
    tarball_name = 'xmlrpc-c-{}.tgz'.format(version)
    fullname = '{}/{}@{}/{}'.format(name, version, user, channel)
    dirname = 'xmlrpc-c-{}'.format(version)
    requires = tuple(to_full_package_name(dep) for dep in deps)
    default_options = ('libcurl:shared=False',)
    exports_sources = "*.in"

    def source(self):
        tools.download(self.tarball_url, self.tarball_name)
        tools.untargz(self.tarball_name)
        self.exports_sources.append("*.in")

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

    def get_helper(self):
        if not hasattr(self, 'helper'):
            if self.settings.os == 'Windows':
                if self.settings.compiler == 'Visual Studio':
                    self.helper = ConanPackageHelper_Msvc(self)
                else:
                    self.helper = ConanPackageHelper_Mingw(self)
            else:
                self.helper = ConanPackageHelper_Autotools(self)
        return self.helper

    def build(self):
        self.get_helper().build()

    def package(self):
        self.get_helper().package()

    def join_path(self, path, *paths):
        helper = self.get_helper()
        if hasattr(helper, 'join_path'):
            return helper.join_path(path, *paths)
        return os.path.join(path, *paths)

    def replace_in_file(self, *args, **kargs):
        return tools.replace_in_file(*args, **kargs)

# TODO
class ConanPackageHelper_Msvc(object):

    def __init__(self, conan_file):
        self.conan_file = conan_file

    def build(self):
        pass

    def package(self):
        self.conan_file.copy('*.h', src='{}/{}'.format(self.conan_file.dirname, 'include'), dst='include')
        self.conan_file.copy('*.hpp', src='{}/{}'.format(self.conan_file.dirname, 'include'), dst='include')
        self.conan_file.copy('*.so', dst='lib', keep_path=False)
        self.conan_file.copy('*.dll', dst='lib', keep_path=False)
        self.conan_file.copy('*.lib', dst='lib', keep_path=False)
        self.conan_file.copy('*.a', dst='lib', keep_path=False)


class ConanPackageHelper_Autotools(object):

    def __init__(self, conan_file = None):
        self.conan_file = conan_file

    def build(self):
        os.chdir(self.conan_file.dirname)
        for p, v in vars(self.conan_file.deps_cpp_info['libcurl']).items():
            print(p, ": ", v)
        generate_curl_config(self.conan_file)
        print("Generated curl_config!")
        #curl_config = '"{}/curl-config"'.format(self.conan_file.deps_cpp_info['libcurl']._bin_paths[0])
        curl_config = '"{}/curl-config"'.format(self.conan_file.rootpath)
        #self.conan_file.run('chmod +x {}'.format(curl_config))
        self.conan_file.run('CPPFLAGS=-I{} LDFLAGS=-L{} CURL_CONFIG={} bash -c "./configure --enable-curl-client"'.format(
            self.conan_file.deps_cpp_info['libcurl'].include_paths[0],
            self.conan_file.deps_cpp_info['libcurl'].lib_paths[0],
            curl_config
            )
        )
        # without this, the makefile won't find the curl-config from the libcurl pkg
        tools.replace_in_file('lib/curl_transport/Makefile', 'shell curl-config', 'shell ' + curl_config)
        self.conan_file.run('make')

    def package(self):
        if platform.system() == 'Linux':
            build_dir = os.path.abspath('{}/../../build'.format(self.conan_file.package_folder))
            self.conan_file.run('find {} -xtype l -delete'.format(build_dir))
            self.conan_file.run('find {} -name "{}" -delete'.format(build_dir, 'blddir'))
            self.conan_file.run('find {} -name "{}" -delete'.format(build_dir, 'srcdir'))
        self.conan_file.copy('*.h', src='{}/{}'.format(self.conan_file.dirname, 'include'), dst='include')
        self.conan_file.copy('*.hpp', src='{}/{}'.format(self.conan_file.dirname, 'include'), dst='include')
        self.conan_file.copy('*.so', dst='lib', keep_path=False)
        self.conan_file.copy('*.dll', dst='lib', keep_path=False)
        self.conan_file.copy('*.lib', dst='lib', keep_path=False)
        self.conan_file.copy('*.a', dst='lib', keep_path=False)

class ConanPackageHelper_Mingw(object):
    
    def __init__(self, conan_file = None):
        self.conan_file = conan_file

    def join_path(self, path, *paths):
        all_paths = [tools.unix_path(path)]
        all_paths.extend(tools.unix_path(p) for p in paths)
        return '/'.join(all_paths)

    def windows_aware_run(self, command):
        return tools.run_in_windows_bash(self.conan_file, command)

    def build(self):
        os.chdir(self.conan_file.dirname)

        # Calculating correct pathnames
        include_paths = self.deps_cpp_info['libcurl'].includedirs
        lib_paths = self.deps_cpp_info['libcurl'].libdirs
        curl_config = '"{}"'.format(
            self.join_path(
                self.deps_cpp_info['libcurl'].rootpath, 
                self.deps_cpp_info['libcurl'].bindirs[0],
                'curl-config'
        ))

        # Configuring
        self.windows_aware_run('CPPFLAGS=-I{} LDFLAGS=-L{} CURL_CONFIG={} bash -c "./configure --enable-curl-client"'.format(
            include_paths[0], lib_paths[0], curl_config)
        )

        # without this, the makefile won't find the curl-config from the libcurl pkg
        tools.replace_in_file('lib/curl_transport/Makefile', 'shell curl-config', 'shell ' + curl_config)
        self.windows_aware_run('make LN_S="cp -r"')

    def package(self):
        self.conan_file.copy('*.h', src='{}/{}'.format(self.conan_file.dirname, 'include'), dst='include')
        self.conan_file.copy('*.hpp', src='{}/{}'.format(self.conan_file.dirname, 'include'), dst='include')
        self.conan_file.copy('*.so', dst='lib', keep_path=False)
        self.conan_file.copy('*.dll', dst='lib', keep_path=False)
        self.conan_file.copy('*.lib', dst='lib', keep_path=False)
        self.conan_file.copy('*.a', dst='lib', keep_path=False)


def get_curl_versionnum(version):
    import re
    components = version.split('.')
    patch_component = components[2]
    major = int(components[0])
    minor = int(components[1])
    patch = int(re.search('[0-9]+', components[2]).group())
    num = major * (256*256) + minor * 256 + patch
    hexnum = '{:06x}'.format(num)
    return hexnum

def generate_curl_config(conan_file):
    from shutil import copy

    # Gathering data
    project_rootpath = conan_file.cpp_info.rootpath
    src_path = conan_file.join_path(project_rootpath, "curl-config.in")
    dst_path = conan_file.join_path(conan_file.conanfile_directory, "curl-config")
    libcurl_info = conan_file.deps_cpp_info['libcurl']
    libcurl_dep_info = get_dep('libcurl')
    libcurl_rootpath = libcurl_info.rootpath
    libcurl_includepath = libcurl_info.include_paths[0]
    libcurl_libpath = libcurl_info.lib_paths[0]

    # Preparing new executable
    #print('"{}" -> "{}"'.format(src_path, dst_path), conan_file.conanfile_directory)
    #copy(src_path, dst_path)
    with open(dst_path, 'w') as dst_file: dst_file.write(curl_config_contents)
    conan_file.run('chmod a+x "{}"'.format(dst_path))
        
    # "Compiling"?
    print("Compiling conan_config...")
    conan_file.replace_in_file(dst_path, "@prefix@", libcurl_info.rootpath)
    conan_file.replace_in_file(dst_path, "@exec_prefix@", project_rootpath)
    conan_file.replace_in_file(dst_path, "@includedir@", libcurl_includepath)
    conan_file.replace_in_file(dst_path, "@libdir@", libcurl_libpath)
    conan_file.replace_in_file(dst_path, "@CONFIGURE_OPTIONS@", "")

    if conan_file.settings.compiler == 'Visual Studio':
        conan_file.replace_in_file(dst_path, "@libext@", "lib")
    else:
        conan_file.replace_in_file(dst_path, "@libext@", "a")

    # TODO See if we can really ignore @REQUIRE_LIB_DEPS@ and @LIBCURL_LIBS@
    # Maybe a solution is to iterate over all transitive dependencies of libcurl and add all of their
    # staticlib versions if libcurl itself is being built as a static library.
    conan_file.replace_in_file(dst_path, "@REQUIRE_LIB_DEPS@", "")
    conan_file.replace_in_file(dst_path, "@LIBCURL_LIBS@", "")
    conan_file.replace_in_file(dst_path, "@LDFLAGS@", "")

    if not hasattr(libcurl_info.options, 'shared') or not libcurl_info.options.shared:
        conan_file.replace_in_file(dst_path, "@CPPFLAG_CURL_STATICLIB@", "-DCURL_STATICLIB")
        conan_file.replace_in_file(dst_path, "@ENABLE_STATIC@", "yes")
        conan_file.replace_in_file(dst_path, "@ENABLE_SHARED@", "no")
    else:
        conan_file.replace_in_file(dst_path, "@CPPFLAG_CURL_STATICLIB@", "")
        conan_file.replace_in_file(dst_path, "@ENABLE_STATIC@", "no")
        conan_file.replace_in_file(dst_path, "@ENABLE_SHARED@", "yes")
    conan_file.replace_in_file(dst_path, "@CURL_CA_BUNDLE@", conan_file.join_path(libcurl_rootpath, "cacert.pem"))
    
    # TODO Check for better options for these
    conan_file.replace_in_file(dst_path, "@CC@", str(conan_file.settings.compiler))
    conan_file.replace_in_file(dst_path, "@SUPPORT_FEATURES@", "IPv6 UnixSockets AsynchDNS")
    conan_file.replace_in_file(dst_path, "@SUPPORT_PROTOCOLS@", "DICT FILE FTP GOPHER HTTP IMAP POP3 RTSP SMTP TELNET TFTP")
    #/todo

    conan_file.replace_in_file(dst_path, "@CURLVERSION@", libcurl_dep_info['version'])
    conan_file.replace_in_file(dst_path, "@VERSIONNUM@", get_curl_versionnum(libcurl_dep_info['version']))


curl_config_contents = """
#! /bin/sh
#***************************************************************************
#                                  _   _ ____  _
#  Project                     ___| | | |  _ \| |
#                             / __| | | | |_) | |
#                            | (__| |_| |  _ <| |___
#                             \___|\___/|_| \_\_____|
#
# Copyright (C) 2001 - 2012, Daniel Stenberg, <daniel@haxx.se>, et al.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at https://curl.haxx.se/docs/copyright.html.
#
# You may opt to use, copy, modify, merge, publish, distribute and/or sell
# copies of the Software, and permit persons to whom the Software is
# furnished to do so, under the terms of the COPYING file.
#
# This software is distributed on an "AS IS" basis, WITHOUT WARRANTY OF ANY
# KIND, either express or implied.
#
###########################################################################

prefix=@prefix@
exec_prefix=@exec_prefix@
includedir=@includedir@
cppflag_curl_staticlib=@CPPFLAG_CURL_STATICLIB@

usage()
{
    cat <<EOF
Usage: curl-config [OPTION]

Available values for OPTION include:

  --built-shared says 'yes' if libcurl was built shared
  --ca        ca bundle install path
  --cc        compiler
  --cflags    pre-processor and compiler flags
  --checkfor [version] check for (lib)curl of the specified version
  --configure the arguments given to configure when building curl
  --features  newline separated list of enabled features
  --help      display this help and exit
  --libs      library linking information
  --prefix    curl install prefix
  --protocols newline separated list of enabled protocols
  --static-libs static libcurl library linking information
  --version   output version information
  --vernum    output the version information as a number (hexadecimal)
EOF

    exit $1
}

if test $# -eq 0; then
    usage 1
fi

while test $# -gt 0; do
    case "$1" in
    # this deals with options in the style
    # --option=value and extracts the value part
    # [not currently used]
    -*=*) value=`echo "$1" | sed 's/[-_a-zA-Z0-9]*=//'` ;;
    *) value= ;;
    esac

    case "$1" in
    --built-shared)
        echo @ENABLE_SHARED@
        ;;

    --ca)
        echo @CURL_CA_BUNDLE@
        ;;

    --cc)
        echo "@CC@"
        ;;

    --prefix)
        echo "$prefix"
        ;;

    --feature|--features)
        for feature in @SUPPORT_FEATURES@ ""; do
            test -n "$feature" && echo "$feature"
        done
        ;;

    --protocols)
        for protocol in @SUPPORT_PROTOCOLS@; do
            echo "$protocol"
        done
        ;;

    --version)
        echo libcurl @CURLVERSION@
        exit 0
        ;;

    --checkfor)
        checkfor=$2
        cmajor=`echo $checkfor | cut -d. -f1`
        cminor=`echo $checkfor | cut -d. -f2`
        # when extracting the patch part we strip off everything after a
        # dash as that's used for things like version 1.2.3-CVS
        cpatch=`echo $checkfor | cut -d. -f3 | cut -d- -f1`
        checknum=`echo "$cmajor*256*256 + $cminor*256 + ${cpatch:-0}" | bc`
        numuppercase=`echo @VERSIONNUM@ | tr 'a-f' 'A-F'`
        nownum=`echo "obase=10; ibase=16; $numuppercase" | bc`

        if test "$nownum" -ge "$checknum"; then
          # silent success
          exit 0
        else
          echo "requested version $checkfor is newer than existing @CURLVERSION@"
          exit 1
        fi
        ;;

    --vernum)
        echo @VERSIONNUM@
        exit 0
        ;;

    --help)
        usage 0
        ;;

    --cflags)
        if test "X$cppflag_curl_staticlib" = "X-DCURL_STATICLIB"; then
          CPPFLAG_CURL_STATICLIB="-DCURL_STATICLIB "
        else
          CPPFLAG_CURL_STATICLIB=""
        fi
        if test "X@includedir@" = "X/usr/include"; then
          echo "$CPPFLAG_CURL_STATICLIB"
        else
          echo "${CPPFLAG_CURL_STATICLIB}-I@includedir@"
        fi
        ;;

    --libs)
        if test "X@libdir@" != "X/usr/lib" -a "X@libdir@" != "X/usr/lib64"; then
           CURLLIBDIR="-L@libdir@ "
        else
           CURLLIBDIR=""
        fi
        if test "X@REQUIRE_LIB_DEPS@" = "Xyes"; then
          echo ${CURLLIBDIR}-lcurl @LIBCURL_LIBS@
        else
          echo ${CURLLIBDIR}-lcurl
        fi
        ;;

    --static-libs)
        if test "X@ENABLE_STATIC@" != "Xno" ; then
          echo @libdir@/libcurl.@libext@ @LDFLAGS@ @LIBCURL_LIBS@
        else
          echo "curl was built with static libraries disabled" >&2
          exit 1
        fi
        ;;

    --configure)
        echo @CONFIGURE_OPTIONS@
        ;;

    *)
        echo "unknown option: $1"
        usage 1
        ;;
    esac
    shift
done

exit 0
"""
