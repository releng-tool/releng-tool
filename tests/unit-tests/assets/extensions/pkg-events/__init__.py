import json
import os
import time


def releng_setup(app):
    app.connect('package-bootstrap-finished', on_pkg_bootstrap_finished)
    app.connect('package-bootstrap-started', on_pkg_bootstrap_started)
    app.connect('package-build-finished', on_pkg_build_finished)
    app.connect('package-build-started', on_pkg_build_started)
    app.connect('package-configure-finished', on_pkg_configure_finished)
    app.connect('package-configure-started', on_pkg_configure_started)
    app.connect('package-install-finished', on_pkg_install_finished)
    app.connect('package-install-started', on_pkg_install_started)
    app.connect('package-postprocess-finished', on_pkg_postprocess_finished)
    app.connect('package-postprocess-started', on_pkg_postprocess_started)


def on_pkg_bootstrap_finished(env):
    capture_pkg_event(env, 'package-bootstrap-finished')


def on_pkg_bootstrap_started(env):
    capture_pkg_event(env, 'package-bootstrap-started')


def on_pkg_build_finished(env):
    capture_pkg_event(env, 'package-build-finished')


def on_pkg_build_started(env):
    capture_pkg_event(env, 'package-build-started')


def on_pkg_configure_finished(env):
    capture_pkg_event(env, 'package-configure-finished')


def on_pkg_configure_started(env):
    capture_pkg_event(env, 'package-configure-started')


def on_pkg_install_finished(env):
    capture_pkg_event(env, 'package-install-finished')


def on_pkg_install_started(env):
    capture_pkg_event(env, 'package-install-started')


def on_pkg_postprocess_finished(env):
    capture_pkg_event(env, 'package-postprocess-finished')


def on_pkg_postprocess_started(env):
    capture_pkg_event(env, 'package-postprocess-started')


def capture_pkg_event(env, name):
    state_file = os.path.join(env['ROOT_DIR'], 'events.json')

    # reload previous state
    try:
        with open(state_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # append new event
    with open(state_file, 'w') as f:
        data[name] = time.monotonic_ns()
        json.dump(data, f)
