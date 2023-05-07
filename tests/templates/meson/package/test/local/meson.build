project(
    'testapp',
    'cpp',
    version : '2.0.0',
)

cpp = meson.get_compiler('cpp')
testlib = cpp.find_library('testlib', required : true)

sources = [
    'main.cpp',
]

dependencies = [
    testlib,
]

executable(
    'testapp',
    sources,
    dependencies: dependencies,
    install: true,
)
