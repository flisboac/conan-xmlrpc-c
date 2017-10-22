cmake_minimum_required(VERSION 3.5)
project(xmlrpc-c-test LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# TODO Fix build for C++
# C++ build not working for the new (C++2) C++ interface, because:
# - server.cpp:(.text.startup+0xec): undefined reference to `xmlrpc_c::registry::addMethod(std::string, xmlrpc_c::methodPtr)'
# - client.cpp:(.text.startup+0xb7): undefined reference to `xmlrpc_c::clientSimple::call(std::string, std::string, std::string, xmlrpc_c::value*, ...)'
#add_executable(hello_server_cpp server.cpp)
#add_executable(hello_client_cpp client.cpp)
#target_link_libraries(hello_server_cpp CONAN_PKG::xmlrpc-c)
#target_link_libraries(hello_client_cpp CONAN_PKG::xmlrpc-c)


add_executable(hello_server_c server.c)
add_executable(hello_client_c client.c)
target_link_libraries(hello_server_c CONAN_PKG::xmlrpc-c)
target_link_libraries(hello_client_c CONAN_PKG::xmlrpc-c)

