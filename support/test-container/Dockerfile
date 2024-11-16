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
    libxcrypt-compat \
    mercurial \
    meson \
    openssl-1.1 \
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

RUN pyenv install 2.7
# RUN CPPFLAGS="-I/usr/include/openssl-1.1" LDFLAGS="-L/usr/lib/openssl-1.1" \
#   pyenv install 3.4
RUN pyenv install 3.5
RUN pyenv install 3.6
RUN pyenv install 3.7
RUN pyenv install 3.8
RUN pyenv install 3.9
RUN pyenv install 3.10
RUN pyenv install 3.11
RUN pyenv install 3.12
RUN pyenv install 3.13
RUN pyenv install 3.14-dev
RUN pyenv install pypy2
RUN pyenv install pypy3

RUN pyenv local \
    2.7 3.5 3.6 3.7 3.8 3.9 3.10 3.11 3.12 3.13 3.14-dev pypy2 pypy3
ENV PATH="$PATH:/home/default/.pyenv/shims"

RUN python3.7 -m pip install "tox<4" "virtualenv<20"
