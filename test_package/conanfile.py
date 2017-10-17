from conans import ConanFile, CMake
from '../conanfile' import ConanPackage

class ConanTestPackage(ConanFile):
   settings = "os", "compiler", "build_type", "arch"
   requires = ConanPackage.fullname # comma separated list of requirements
   generators = "cmake", "gcc", "txt"

   def build(self):
      cmake = CMake(self)
      cmake.configure()
      cmake.build()