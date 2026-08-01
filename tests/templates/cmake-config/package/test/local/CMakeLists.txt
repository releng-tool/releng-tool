cmake_minimum_required(VERSION 3.10)
project(releng-tool-test)

find_package(releng-tool-testlib REQUIRED CONFIG)

add_executable(testapp main.cpp)
target_link_libraries(testapp PUBLIC ${TESTLIB})
target_link_libraries(testapp PRIVATE releng-tool-testlib::releng-tool-testlib)
install(TARGETS testapp DESTINATION bin)
