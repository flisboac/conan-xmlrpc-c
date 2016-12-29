cmake_minimum_required(VERSION 3.0.0)
project(xmlrpc-c-test)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(hello_server server.cpp)
add_executable(hello_client client.cpp)

target_link_libraries(hello_server ${CONAN_LIBS})
set_target_properties(
        hello_server
        PROPERTIES
        CXX_STANDARD 11)
target_link_libraries(hello_client ${CONAN_LIBS})
set_target_properties(
        hello_client
        PROPERTIES
        CXX_STANDARD 11)
