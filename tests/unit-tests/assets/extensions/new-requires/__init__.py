# sample extension will should fail to load since the the required
# version number is newer than the current version
def releng_setup(app):
    app.require_version('999999')
