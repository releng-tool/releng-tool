# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool
#
# Container image used to support unit and tool testing.

FROM archlinux:latest

RUN pacman -Syu \
    base-devel \
    bzr \
    cmake \
    cvs \
    git \
    mercurial \
    meson \
    patch \
    pyenv \
    python-tox \
    rust \
    scons \
    --noconfirm

# setup a default user
# (tools like cvs are not happy when running as root)
RUN useradd -ms /bin/bash default
USER default
WORKDIR /home/default

RUN pyenv install 3.9
RUN pyenv install 3.10
RUN pyenv install 3.11
RUN pyenv install 3.12
RUN pyenv install 3.13
RUN pyenv install 3.14-dev
RUN pyenv install pypy3

RUN pyenv local 3.9 3.10 3.11 3.12 3.13 3.14-dev pypy3
ENV PATH="$PATH:/home/default/.pyenv/shims"
