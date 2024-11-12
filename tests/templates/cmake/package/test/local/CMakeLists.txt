cmake_minimum_required(VERSION 3.5)
project(test)

find_library(TESTLIB testlib REQUIRED)

add_executable(testapp main.cpp)
target_link_libraries(testapp PUBLIC ${TESTLIB})
install(TARGETS testapp DESTINATION bin)
