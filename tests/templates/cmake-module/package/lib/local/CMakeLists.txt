cmake_minimum_required(VERSION 3.10)
project(releng-tool-testlib)
add_library(releng-tool-testlib lib.cpp)
set_target_properties(releng-tool-testlib PROPERTIES PUBLIC_HEADER lib.h)
install(TARGETS releng-tool-testlib
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)
install(FILES example-module-helper.cmake DESTINATION share/cmake/Modules)
