# sample extension that registers on various events
def releng_setup(app):
    app.connect('config-loaded', on_config_event)
    app.connect('post-build-started', on_post_build_started)
    app.connect('post-build-finished', on_post_build_finished)


def on_config_event(env):
    env['last-event'] = 'config-loaded'


def on_post_build_started(env):
    env['last-event'] = 'post-build-started'


def on_post_build_finished(env):
    env['last-event'] = 'post-build-finished'
