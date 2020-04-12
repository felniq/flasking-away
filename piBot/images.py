import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from piBot.db import get_db

bp = Blueprint('images', __name__, url_prefix='/images')


@bp.route('/all', methods=('GET', 'POST'))
def index_images():
    db = get_db()
    error = None
    flash(error)
    return render_template('images/all_images.html')
