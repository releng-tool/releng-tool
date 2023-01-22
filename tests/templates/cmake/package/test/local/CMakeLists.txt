cmake_minimum_required(VERSION 3.1)
project(test)
add_executable(testapp main.cpp)
install(TARGETS testapp DESTINATION bin)
