cmake_minimum_required(VERSION 3.10)
project(releng-tool-testlib)
add_library(releng-tool-testlib lib.cpp)
set_target_properties(releng-tool-testlib PROPERTIES PUBLIC_HEADER lib.h)
target_include_directories(releng-tool-testlib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include-variant>
)
install(TARGETS releng-tool-testlib
    EXPORT releng-tool-testlibTargets
    ARCHIVE DESTINATION lib-variant
    LIBRARY DESTINATION lib-variant
    PUBLIC_HEADER DESTINATION include-variant
)
install(EXPORT releng-tool-testlibTargets
    FILE releng-tool-testlibConfig.cmake
    NAMESPACE releng-tool-testlib::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/releng-tool-testlib
)
