cmake_minimum_required(VERSION 3.5)
project(testlib)
add_library(testlib lib.cpp)
set_target_properties(testlib PROPERTIES PUBLIC_HEADER lib.h)
install(TARGETS testlib
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)
install(FILES example-module-helper.cmake DESTINATION share/cmake/Modules)
