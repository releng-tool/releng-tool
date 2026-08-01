cmake_minimum_required(VERSION 3.10)
project(releng-tool-test)

# cmake should be able to automatically load registered module from
# a dependent project
include(example-module-helper)

find_library(TESTLIB NAMES releng-tool-testlib REQUIRED)

add_executable(testapp main.cpp)
target_link_libraries(testapp PUBLIC ${TESTLIB})
install(TARGETS testapp DESTINATION bin)
