import os
from flask import Flask
from werkzeug.routing import BaseConverter


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'piBot.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    cache_folder = os.path.join('static', 'cache')
    image_folder = os.path.join('nasse', 'images')
    app.config['CACHE_FOLDER'] = cache_folder
    app.config['IMAGE_FOLDER'] = image_folder

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    try:
        os.makedirs(cache_folder)
    except OSError:
        pass

    class RegexConverter(BaseConverter):
        def __init__(self, url_map, *items):
            super(RegexConverter, self).__init__(url_map)
            self.regex = items[0]

    app.url_map.converters['regex'] = RegexConverter

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import images
    app.register_blueprint(images.bp)

    return app
