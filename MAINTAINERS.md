# MAINTAINERS

This document serves as a guide for maintainers. For users wishes to contribute
to this repository, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## Quirk checks

To quickly lint the source:

```
./lint
```

To perform a single unit test run:

```
./check
```

To perform a single tools test run:

```
./tool-check
```

## Full checks

Before any release, the following check script should be run to verify all
expected interpreters and tool checks pass:

```
./scripts/task-full-check.sh
```

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

## Coverage runs

To generate a coverage report, run the following:

```
./scripts/task-coverage.sh
```

For a multi-platform coverage data set, run the following in order:

```
(from a Linux machine with a Window volume mount, invoke)
./scripts/task-coverage-container.sh

(then from a Windows machine, invoke)
./scripts/task-coverage.sh --no-clean
```

## Updating SPDX license information

Update the SPDX license version in this configuration file:

```
./scripts/spdx-license-data.ini
```

Then update the internal SPDX license database by running:

```
./scripts/update-spdx-license-data.py
```
