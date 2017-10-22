from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class ConanPackage(ConanFile):

    short_paths = True
    build_policy = "missing"

    name = 'xmlrpc-c'
    description = 'A lightweight RPC library based on XML and HTTP.'
    version = '1.39.12'
    license = 'BSD-3-Clause'
    distname = 'conan-{}'.format(name)
    url = 'https://github.com/flisboac/{}'.format(distname)
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
    }
    default_options = (
        'shared=False',
        'libcurl:shared=False',
    )
    requires = (
        'libcurl/7.50.3@lasote/testing',
        #'OpenSSL/1.0.2l@conan/stable',
        #'zlib/1.2.11@conan/stable'
    )

    dirname = '{}-{}'.format(name, version)

    def __init__(self, *args, **kargs):
        ConanFile.__init__(self, *args, **kargs)
        self._helper = None

    def source(self):
        tarball_name = '{}.tgz'.format(self.dirname)
        tarball_url = (
            'https://sourceforge.net/projects/xmlrpc-c/files/Xmlrpc-c%20Super%20Stable/{}/{}'.format(
                self.version, tarball_name))
        tools.download(tarball_url, tarball_name)
        tools.untargz(tarball_name)

    def package_info(self): 
        self.cpp_info.libs = [
            'xmlrpc_client++',
            'xmlrpc_client',
            'xmlrpc_server_pstream++',
            'xmlrpc_server_cgi++',
            'xmlrpc_server_cgi',
            'xmlrpc_server_abyss++',
            'xmlrpc_server_abyss',
            'xmlrpc_server++',
            'xmlrpc_server',
            'xmlrpc_abyss',
            'xmlrpc_client',
            'xmlrpc_server',
            'xmlrpc_server_abyss',
            'xmlrpc_cpp',
            'xmlrpc++',
            'xmlrpc_util++',
            'xmlrpc',
            'xmlrpc_xmlparse',
            'xmlrpc_xmltok',
            'xmlrpc_util',
            #'pthread',
            #'curl', # Comes from depmgmt
            'xmlrpc_packetsocket'
        ]
        if not self.settings.os == "Windows":
            #self.cpp_info.cppflags = ["-pthread"] # NOT WORKING
            self.cpp_info.libs.append("pthread")

    def package(self):
        if self.settings.os == 'Linux':
            build_dir = os.path.abspath(r'{}/../../build'.format(self.package_folder))
            self.run('find {} -xtype l -delete'.format(build_dir))
            self.run('find {} -name "{}" -delete'.format(build_dir, 'blddir'))
            self.run('find {} -name "{}" -delete'.format(build_dir, 'srcdir'))

        self.copy('*.h', src='{}/{}'.format(self.dirname, 'include'), dst='include')
        self.copy('*.hpp', src='{}/{}'.format(self.dirname, 'include'), dst='include')
       
        if self.options.shared:
            self.copy('*.so', dst='lib', keep_path=False)
            self.copy('*.dll', dst='lib', keep_path=False)
        else:
            self.copy('*.lib', dst='lib', keep_path=False)
            self.copy('*.a', dst='lib', keep_path=False)
    
    def build(self):
        self.get_helper().build()

    def get_curl_config_location(self):
        return self.join_path(self.conanfile_directory, "curl-config")

    def get_helper(self):
        if not self._helper:
            if self.settings.os == 'Windows':
                if self.settings.compiler == 'Visual Studio':
                    self._helper = ConanPackageHelper_Msvc(self)
                else:
                    self._helper = ConanPackageHelper_Mingw(self)
            else:
                self._helper = ConanPackageHelper_Autotools(self)
        return self._helper

    def join_path(self, path, *paths):
        helper = self.get_helper()
        if hasattr(helper, 'join_path'):
            return helper.join_path(path, *paths)
        return os.path.join(path, *paths)

    def replace_in_file(self, *args, **kargs):
        return tools.replace_in_file(*args, **kargs)

    def sh_run(self, cmd):
        helper = self.get_helper()
        if hasattr(helper, 'sh_run'):
            return helper.sh_run(cmd)
        return self.run(cmd)


# TODO MSVC build, using the .bat files and all that
class ConanPackageHelper_Msvc(object):

    def __init__(self, conan_file):
        self.conan_file = conan_file

    def build(self):
        pass


class ConanPackageHelper_Autotools(object):

    def __init__(self, conan_file = None):
        self.conan_file = conan_file

    def build(self):
        os.chdir(self.conan_file.dirname)
        
        if self.conan_file.settings.build_type == "Debug":
            # TODO Check how I can include a debug configuration in this case (e.g. a portable -g?)
            # The xmlrpc-c's scripts don't seem to offer such a facility.
            pass

        generate_curl_config(self.conan_file)

        env_build = AutoToolsBuildEnvironment(self.conan_file)
        curl_config = self.conan_file.get_curl_config_location()
        env_vars = merge_dicts(env_build.vars, { 'CURL_CONFIG': curl_config })

        configure_options = "--enable-curl-client"

        with tools.environment_append(env_vars):
            self.conan_file.sh_run(r'./configure {}'.format(configure_options))
            tools.replace_in_file(r'lib/curl_transport/Makefile', 'shell curl-config', 'shell "{}"'.format(
                curl_config))
            self.conan_file.sh_run('make')


# TODO Check if this works
class ConanPackageHelper_Mingw(ConanPackageHelper_Autotools):
    
    def join_path(self, path, *paths):
        all_paths = [tools.unix_path(path)]
        all_paths.extend(tools.unix_path(p) for p in paths)
        return '/'.join(all_paths)

    def sh_run(self, command):
        return tools.run_in_windows_bash(self.conan_file, command)


def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args: 
        result.update(dictionary)
    return result

def get_curl_versionnum(version):
    import re
    components = version.split('.')
    major = int(components[0])
    minor = int(components[1])
    patch = int(re.search('[0-9]+', components[2]).group())
    num = major * (256*256) + minor * 256 + patch
    hexnum = '{:06x}'.format(num)
    return hexnum

def generate_curl_config(conan_file):

    # Gathering data
    project_rootpath = conan_file.cpp_info.rootpath
    dst_path = conan_file.get_curl_config_location()
    libcurl_info = conan_file.deps_cpp_info['libcurl']
    libcurl_dep_info = conan_file.requires['libcurl'].conan_reference
    libcurl_version = libcurl_dep_info.version
    libcurl_rootpath = libcurl_info.rootpath
    libcurl_includepath = libcurl_info.include_paths[0]
    libcurl_libpath = libcurl_info.lib_paths[0]

    # Preparing new executable
    tools.save(dst_path, curl_config_contents)
    conan_file.run('chmod a+x "{}"'.format(dst_path))
        
    # "Compiling"?
    conan_file.replace_in_file(dst_path, r"@prefix@", libcurl_info.rootpath)
    conan_file.replace_in_file(dst_path, r"@exec_prefix@", project_rootpath)
    conan_file.replace_in_file(dst_path, r"@includedir@", libcurl_includepath)
    conan_file.replace_in_file(dst_path, r"@libdir@", libcurl_libpath)
    conan_file.replace_in_file(dst_path, r"@CONFIGURE_OPTIONS@", "")

    if conan_file.settings.compiler == 'Visual Studio':
        conan_file.replace_in_file(dst_path, r"@libext@", "lib")
    else:
        conan_file.replace_in_file(dst_path, r"@libext@", "a")

    # TODO See if we can really ignore @REQUIRE_LIB_DEPS@ and @LIBCURL_LIBS@
    # Maybe a solution is to iterate over all transitive dependencies of libcurl and add all of their
    # staticlib versions if libcurl itself is being built as a static library.
    conan_file.replace_in_file(dst_path, r"@REQUIRE_LIB_DEPS@", "")
    conan_file.replace_in_file(dst_path, r"@LIBCURL_LIBS@", "")
    conan_file.replace_in_file(dst_path, r"@LDFLAGS@", "")

    if not hasattr(libcurl_info.options, 'shared') or not libcurl_info.options.shared:
        conan_file.replace_in_file(dst_path, r"@CPPFLAG_CURL_STATICLIB@", "-DCURL_STATICLIB")
        conan_file.replace_in_file(dst_path, r"@ENABLE_STATIC@", "yes")
        conan_file.replace_in_file(dst_path, r"@ENABLE_SHARED@", "no")
    else:
        conan_file.replace_in_file(dst_path, r"@CPPFLAG_CURL_STATICLIB@", "")
        conan_file.replace_in_file(dst_path, r"@ENABLE_STATIC@", "no")
        conan_file.replace_in_file(dst_path, r"@ENABLE_SHARED@", "yes")

    conan_file.replace_in_file(dst_path, r"@CURL_CA_BUNDLE@",
            conan_file.join_path(libcurl_rootpath, "cacert.pem"))
    
    # TODO Check for better options for these
    conan_file.replace_in_file(dst_path, r"@CC@", str(conan_file.settings.compiler))
    conan_file.replace_in_file(dst_path, r"@SUPPORT_FEATURES@", "IPv6 UnixSockets AsynchDNS")
    conan_file.replace_in_file(dst_path, r"@SUPPORT_PROTOCOLS@", 
            "DICT FILE FTP GOPHER HTTP IMAP POP3 RTSP SMTP TELNET TFTP")
    #/todo

    conan_file.replace_in_file(dst_path, r"@CURLVERSION@", libcurl_version)
    conan_file.replace_in_file(dst_path, r"@VERSIONNUM@", get_curl_versionnum(libcurl_version))


curl_config_contents = r"""
#! /bin/sh:
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
