from flask import Blueprint, render_template, redirect, request
from flask_login import login_required
from app.dao.headrent import get_headrent, get_headrents
from app.dao.common import get_combodict_basic, get_hr_statuses

headrent_bp = Blueprint('headrent_bp', __name__)


@headrent_bp.route('/headrents', methods=['GET', 'POST'])
def headrents():
    filterdict, headrents = get_headrents()
    hr_statuses = get_hr_statuses()
    hr_statuses.insert(0, "all statuses")

    return render_template('headrents.html', filterdict=filterdict, headrents=headrents, hr_statuses=hr_statuses)


@headrent_bp.route('/headrent/<int:id>', methods=["GET", "POST"])
@login_required
def headrent(id):
    headrent = get_headrent(id)
    combodict = get_combodict_basic()
    #gather combobox values in a dictionary
    hr_statuses = get_hr_statuses()

    return render_template('headrent.html', combodict=combodict, headrent=headrent, hr_statuses=hr_statuses)
