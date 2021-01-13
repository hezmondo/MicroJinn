from flask import Blueprint, render_template, redirect, request
from flask_login import login_required
from app.dao.headrent import get_headrent, get_headrents
from app.dao.common import get_combodict

hr_bp = Blueprint('hr_bp', __name__)

@hr_bp.route('/headrents', methods=['GET', 'POST'])
def headrents():
    headrents, statusdets = get_headrents()

    return render_template('headrents.html', headrents=headrents, statusdets=statusdets)


@hr_bp.route('/headrent/<int:id>', methods=["GET", "POST"])
@login_required
def headrent(id):
    headrent = get_headrent(id)
    combodict = get_combodict("basic")
    #gather basic combobox values in a dictionary

    return render_template('headrent.html', combodict=combodict, headrent=headrent)
