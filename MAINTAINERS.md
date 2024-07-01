# MAINTAINERS

This document serves as a guide for maintainers. For users wishes to contribute
to this repository, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## Release commands

Prepare a release tag on the version bump commit:

```shell-session
git tag -s -a v<version> <hash> -m "releng-tool <version>"
git verify-tag <tag>
```

Prepare a release by invoking the following script:

```shell-session
./task-release-prepare
```

Publish the release:

```shell-session
./task-release-publish
```

Push up the release tag:

```shell-session
git push origin <tag>
```

Create a new release entry on GitHub:

```
🛈 [View announcement][announcement] ෴ _https://github.com/releng-tool/releng-tool/compare/v<TAG>...v<TAG>_

<bullet points from changelog>

[announcement]: https://docs.releng.io/news/<announcement-page>/
```
