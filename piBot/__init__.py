import os
import psutil
from gpiozero import CPUTemperature
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
    cache_folder = os.path.join('static', 'nasse' ,'.cache')
    image_folder = os.path.join('static', 'nasse')
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

    @app.route('/system-stats')
    def get_system_stats():
        stat_cpu = "CPU: " + str(psutil.cpu_percent()) + '%'

        cpu = CPUTemperature()
        stat_cpu_temp = "CPU temp: " + str(cpu.temperature)

        memory = psutil.virtual_memory()
        # Divide from Bytes -> KB -> MB
        available = round(memory.available/1024.0/1024.0,1)
        total = round(memory.total/1024.0/1024.0,1)
        stat_mem = "RAM: " + str(available) + 'MB free / ' + str(total) + 'MB total ( ' + str(memory.percent) + '% )'

        disk = psutil.disk_usage('/')
        # Divide from Bytes -> KB -> MB -> GB
        free = round(disk.free/1024.0/1024.0/1024.0,1)
        total = round(disk.total/1024.0/1024.0/1024.0,1)
        stat_disk = "DISK: " + str(free) + 'GB free / ' + str(total) + 'GB total ( ' + str(disk.percent) + '% )'

        return stat_cpu + "<br/>" + stat_cpu_temp + "<br/>" + stat_mem + "<br/>" + stat_disk

    from . import db
    db.init_app(app)

    from . import images
    app.register_blueprint(images.bp)

    return app
