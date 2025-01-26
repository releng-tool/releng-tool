import json
import os


def releng_setup(app):
    app.connect('config-loaded', on_config_event)
    app.connect('post-build-started', on_post_build_started)
    app.connect('post-build-finished', on_post_build_finished)


def on_config_event(env):
    capture_working_directory(env, 'config-loaded')


def on_post_build_started(env):
    capture_working_directory(env, 'post-build-started')


def on_post_build_finished(env):
    capture_working_directory(env, 'post-build-finished')


def capture_working_directory(env, name):
    state_file = os.path.join(env['ROOT_DIR'], name + '.json')
    with open(state_file, 'w') as f:
        json.dump({'wd': os.getcwd()}, f)
