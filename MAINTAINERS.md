# MAINTAINERS

This document serves as a guide for maintainers. For users wishes to contribute
to this repository, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## Release commands

Perform a clean build:

```shell-session
python setup.py clean --all
python setup.py sdist bdist_wheel
```

Sign the packages:

```shell-session
gpg --detach-sign -a dist/releng-tool-*.gz
gpg --detach-sign -a dist/releng-tool-*.whl
```

Publish the packages:

```shell-session
twine upload dist/*
```

Tag/push the release tag:

```shell-session
git tag -s -a v<version> <hash> -m "releng-tool <version>"
git verify-tag <tag>
git push origin <tag>
```
