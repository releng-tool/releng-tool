cmake_minimum_required(VERSION 3.1)
project(testlib)
add_library(testlib lib.cpp)
set_target_properties(testlib PROPERTIES PUBLIC_HEADER lib.h)
install(TARGETS testlib
    LIBRARY DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)
