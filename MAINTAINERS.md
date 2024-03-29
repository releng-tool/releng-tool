# MAINTAINERS

This document serves as a guide for maintainers. For users wishes to contribute
to this repository, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## Release commands

Perform a clean build:

```shell-session
python -m build
```

Verify packages can be published:

```shell-session
twine check dist/*
```

Sign the packages:

```shell-session
gpg --detach-sign -a dist/releng-tool-*.gz
gpg --detach-sign -a dist/releng_tool-*.whl
```

Sanity check the signed packages:

```shell-session
gpg --verify dist/releng-tool-*.gz.asc
gpg --verify dist/releng_tool-*.whl.asc
```

Publish the packages:

```shell-session
twine upload --repository releng-tool dist/*
```

Tag/push the release tag:

```shell-session
git tag -s -a v<version> <hash> -m "releng-tool <version>"
git verify-tag <tag>
git push origin <tag>
```

Generate hashes from the release:

```shell-session
cd dist
sha256sum -b * >releng-tool-<version>.sha256sum
```

Create a new release entry on GitHub:

```
🛈 [View announcement][announcement] ෴ _https://github.com/releng-tool/releng-tool/compare/v<TAG>...v<TAG>_

<bullet points from changelog>

[announcement]: https://docs.releng.io/news/<announcement-page>/
```
