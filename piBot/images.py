import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_from_directory, send_file)
from flask import current_app as app
from werkzeug.security import check_password_hash, generate_password_hash
from PIL import Image

from piBot.db import get_db

bp = Blueprint('images', __name__, url_prefix='/images')


def get_all_files():
    image_list = list()
    for file in os.listdir(os.path.join(app.root_path, app.config['IMAGE_FOLDER'])):
        if file.endswith((".JPG", ".jpg")):
            time = os.path.getmtime(os.path.join(app.root_path, app.config['IMAGE_FOLDER'], file))
            image_list.append([file, int(time)])
    return image_list


def load_folder_to_database(i_list):
    database = get_db()
    i_list = get_all_files()
    filename_list = list()
    for x in i_list:
        filename_list.append(x[0])
        database.execute(
            'INSERT OR IGNORE INTO images (filename, modifieddate)'
            ' VALUES (?, ?)',
            (x[0], x[1])
        )
        database.commit()
    files_to_delete = database.execute(
        f'SELECT id, filename FROM images WHERE filename NOT IN ({str(filename_list).replace("[", "").replace("]", "")})').fetchall()
    if files_to_delete:
        id_list = list()
        for row in files_to_delete:
            id_list.append(row[0])
        database.execute(f'DELETE FROM images WHERE id IN ({str(id_list).replace("[", "").replace("]", "")})')
        database.commit()


def get_images_in_order():
    database = get_db()
    filename_list = list()
    files = database.execute('SELECT filename FROM images ORDER BY modifieddate DESC').fetchall()
    for row in files:
        filename_list.append(row[0])
    return filename_list


def create_thumbnails(filename):
    thumb_width = 600
    thumb_height = 600
    try:
        image = Image.open(os.path.join(app.root_path, app.config['IMAGE_FOLDER'], filename))
        image.thumbnail((thumb_width, thumb_height), Image.ANTIALIAS)
        angle = 0
        out = image.rotate(angle, expand=True)
        out.save(os.path.join(app.root_path, app.config['CACHE_FOLDER'], "thumbnail_" + filename))

    except:
        traceback.print_exc()


@bp.route('/all', methods=('GET', 'POST'))
def index_images():
    i_list = get_all_files()
    load_folder_to_database(i_list)
    image_name_list = get_images_in_order()
    for x in i_list:
        if not os.path.isfile(os.path.join(app.root_path, app.config['CACHE_FOLDER'], "thumbnail_" + x[0])):
            create_thumbnails(x[0])
    error = None
    flash(error)
    # TODO thumbnail all images and make a list of the images in date order
    return render_template('images/all_images.html', image_list=image_name_list)


@bp.route('/dummy', methods=('GET', 'POST'))
def return_file():
    image_name = request.args.get('image_name')
    return send_file(os.path.join(app.root_path, app.config['IMAGE_FOLDER'], image_name),
                     attachment_filename=image_name, as_attachment=True)
