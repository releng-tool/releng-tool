set_allowedmodes("releng_tool_test_mode")

target("releng-tool-test")
    set_kind("binary")
    add_files("main.cpp")
    add_headerfiles("lib.h")
    add_links("releng-tool-testlib")
