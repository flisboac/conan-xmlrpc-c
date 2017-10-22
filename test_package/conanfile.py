import sys, os

from conans import ConanFile, CMake

class ConanTestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "gcc", "txt"
    default_options = ("xmlrpc-c:shared=False", "libcurl:shared=False", "OpenSSL:shared=False")

    def build(self):
       cmake = CMake(self)
       cmake.verbose = True
       cmake.configure()
       cmake.build()

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")
        
    def test(self):
        # TODO Find a better way to test the servers
        # There's not really a way to test this without hanging up the build/test
        # process as a whole. How do we kill the server process once the client
        # has made its (only) call to the server?
        pass

