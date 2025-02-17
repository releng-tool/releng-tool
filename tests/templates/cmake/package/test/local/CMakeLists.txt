cmake_minimum_required(VERSION 3.5)
project(test)

# cmake should be able to automatically load registered module from
# a dependent project
include(example-module-helper)

find_library(TESTLIB testlib REQUIRED)

add_executable(testapp main.cpp)
target_link_libraries(testapp PUBLIC ${TESTLIB})
install(TARGETS testapp DESTINATION bin)
