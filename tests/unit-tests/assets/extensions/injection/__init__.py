def releng_setup(app):
    app.connect('config-loaded', on_config_event)


def on_config_event(env):
    env['custom_method'] = custom_method


def custom_method():
    return 42
