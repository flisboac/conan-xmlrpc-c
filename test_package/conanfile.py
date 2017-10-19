import sys, os

# TODO Open an issue in Conan asking why this does not work
conanfile_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(conanfile_path)
print(conanfile_path)

from conans import ConanFile, CMake
#from conanfile import ConanPackage

class ConanTestPackage(ConanFile):
   settings = "os", "compiler", "build_type", "arch"
   generators = "cmake", "gcc", "txt"
   default_options = ("xmlrpc-c:shared=False", "libcurl:shared=False", "OpenSSL:shared=False")

   def build(self):
      cmake = CMake(self)
      cmake.verbose = True
      cmake.definitions['CFLAGS'] = '-lxmlrpc'
      cmake.definitions['CPPFLAGS'] = 'lxmlrpc -lxmlrpc_cpp'
      cmake.configure()
      cmake.build()

