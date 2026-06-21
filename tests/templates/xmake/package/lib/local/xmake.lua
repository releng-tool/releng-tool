add_rules("mode.debug", "mode.release")

target("releng-tool-testlib")
    set_kind("static")
    add_files("lib.cpp")
    add_headerfiles("lib.h")
