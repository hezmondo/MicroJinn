from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import login_required
from app.dao.landlord import get_landlord_dict, get_landlord, get_landlords, post_landlord

landlord_bp = Blueprint('landlord_bp', __name__)


@landlord_bp.route('/landlord/<int:id>', methods=['GET', 'POST'])
@login_required
def landlord(id):
    if request.method == "POST":
        id = post_landlord(id)

        return redirect(url_for('landlord_bp.property', id=id))

    landlord = get_landlord(id) if id != 0 else {"id": 0}
    landlord_dict = get_landlord_dict()

    return render_template('landlord.html', landlord=landlord, landlord_dict=landlord_dict)


@landlord_bp.route('/landlords', methods=['GET'])
def landlords():
    landlords = get_landlords()

    return render_template('landlords.html', landlords=landlords)

