from flask import Blueprint, render_template,  request
from flask_login import login_required
from app.dao.landlord import get_landlord_dict, get_landlord, get_landlords, post_landlord

la_bp = Blueprint('la_bp', __name__)

@la_bp.route('/landlord/<int:id>', methods=['GET', 'POST'])
@login_required
def landlord(id):
    if request.method == "POST":
        landlord = post_landlord(id)
    else:
        landlord = get_landlord(id)

    landlord_dict = get_landlord_dict()

    return render_template('landlord.html', landlord=landlord, landlord_dict=landlord_dict)

@la_bp.route('/landlords', methods=['GET'])
def landlords():
    landlords = get_landlords()

    return render_template('landlords.html', landlords=landlords)

