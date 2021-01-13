from flask import Blueprint, render_template
from flask_login import login_required
from app.dao.filter import get_rentobjects

ho_bp = Blueprint('ho_bp', __name__)

@ho_bp.route('/', methods=['GET', 'POST'])
@ho_bp.route('/index', methods=['GET', 'POST'])
# @login_required
def index():
    filterdict, rentobjects = get_rentobjects("basic", 0)

    return render_template('home.html', filterdict=filterdict, rentobjects=rentobjects)


