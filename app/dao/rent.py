import json
from app import db
from flask import flash, redirect, url_for, request
from sqlalchemy import func
from sqlalchemy.orm import joinedload, load_only
from app.dao.database import commit_to_database, pop_idlist_recent
from app.models import Jstore, PrHistory, Rent, RentExternal


def check_pr_exists(rent_id):  # check if rent has record in pr_history
    return db.session.query(func.count(PrHistory.rent_id)).filter_by(rent_id=rent_id).scalar()


def create_new_rent():
    # create new rent and property function not yet built, so return id for dummy rent:
    return 23


def get_rent(rent_id):  # returns all Rent member variables plus associated items as a mutable dict
    if rent_id == 0:        # take the user to create new rent function (not yet built)
        rent_id = create_new_rent()
    pop_idlist_recent("recent_rents", rent_id)
    # rent = Rent.query.filter_by(id=rent_id).first()
    rent = db.session.query(Rent) \
        .filter_by(id=rent_id)\
        .options(joinedload('agent').load_only('id', 'detail'),
            joinedload('landlord').options(load_only('name'),
            joinedload('manager').load_only('managername', 'manageraddr', 'manageraddr2'),
            joinedload('money_account').load_only('acc_name', 'acc_num', 'bank_name', 'sort_code')),
            joinedload('typedeed').load_only('deedcode', 'info')) \
        .one_or_none()
    if rent is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))

    return rent


def get_rent_md(rent_id):  # returns 5 Rent member variables as a mutable dict for mail_dialog
    return db.session.query(Rent) \
        .filter_by(id=rent_id).options(load_only('id', 'agent_id', 'datecode_id',
                                                 'mailto_id', 'rentcode', 'tenantname')) \
        .one_or_none()


def get_rent_external(rent_id):
    return db.session.query(RentExternal) \
        .filter_by(id=rent_id).options(joinedload('manager_external').load_only('codename', 'detail')) \
        .one_or_none()


# def getrents_basic(filtr):        # simple filtered rents for main rents page
#     return Property.query \
#         .join(Rent) \
#         .outerjoin(Agent) \
#         .with_entities(Rent.id, Agent.detail, Rent.arrears, Rent.freq_id, Rent.lastrentdate,
#                        func.mjinn.prop_addr(Rent.id).label('propaddr'),
#                        Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname) \
#         .filter(*filtr).limit(50).all()


def getrents_basic(filtr):        # simple filtered rents for main rents page
    return db.session.query(Rent) \
        .options(load_only('id', 'rentcode', 'arrears', 'datecode_id', 'freq_id', 'lastrentdate',
                           'rentpa', 'source', 'status_id', 'tenantname'),
             joinedload('agent').load_only('detail'),) \
        .filter(*filtr).order_by(Rent.rentcode).limit(30).all()


# def getrents_advanced(filtr, runsize):    # filtered rents for advanced queries and payrequest pages
#     return Rent.query \
#         .join(Landlord) \
#         .outerjoin(Agent) \
#         .with_entities(Rent.id, Rent.advarr_id, Rent.arrears, Rent.freq_id, Rent.lastrentdate,
#                        func.mjinn.prop_addr(Rent.id).label('propaddr'),
#                        Rent.prdelivery_id, Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname,
#                        Agent.detail, Landlord.name, Property.propaddr)  \
#         .filter(*filtr).order_by(Rent.rentcode).limit(runsize).all()
#

def getrents_advanced(filtr, runsize):    # filtered rents for advanced queries and payrequest pages
    return db.session.query(Rent) \
        .options(load_only('id', 'advarr_id', 'arrears', 'freq_id', 'lastrentdate',
                                                        'prdelivery_id', 'rentcode', 'rentpa', 'tenantname'),
           joinedload('landlord').load_only('name'),
           joinedload('agent').load_only('detail')) \
        .filter(*filtr).limit(runsize).all()


def get_rentsexternal(filtr):     # simple filtered external rents for main rents page or external rents page
    return db.session.query(RentExternal) \
            .options(load_only('id', 'agentdetail', 'arrears', 'datecode_id', 'lastrentdate', 'rentcode', 'owner',
                               'propaddr', 'rentpa', 'source', 'status', 'tenantname'),
                     joinedload('manager_external').load_only('codename')) \
            .filter(*filtr).order_by(RentExternal.rentcode).limit(30).all()


def get_rents_filters(typ):        # get stored advanced filter for advanced queries and payrequest pages
    filters = Jstore.query.filter(Jstore.type == typ).all()

    return filters


def post_rent_agent_unlink(rent_id):
    rent = Rent.query.get(rent_id)
    rent.agent_id = None
    # change mailto to tenant
    if rent.mailto_id == 1 or 2:
        rent.mailto_id = 3
    commit_to_database()


def post_rent_agent_update(agent_id, rent_id):
    rent = Rent.query.get(rent_id)
    rent.agent_id = agent_id
    # change mailto to agent
    rent.mailto_id = 1
    commit_to_database()


def post_rent_filter(filterdict):
    # save this filter dictionary in jstore
    print("filterdict during save")
    print(filterdict)
    jname = request.form.get("filtername")
    jtype = request.form.get("filtertype")
    if jtype == "payrequest":
        jtype = 1
    elif jtype == "rentprop":
        jtype = 2
    else:
        jtype = 3
    j_id = \
        Jstore.query.with_entities(Jstore.id).filter \
            (Jstore.code == jname).one_or_none()
    if j_id:
        j_id = j_id[0]
        jstore = Jstore.query.get(j_id)
    else:
        jstore = Jstore()
    jstore.type = jtype
    jstore.code = jname
    jstore.content = json.dumps(filterdict)
    db.session.add(jstore)
    commit_to_database()


def post_rent(rent):
    db.session.add(rent)
    db.session.flush()
    rent_id = rent.id
    commit_to_database()

    return rent_id

# def update_roll_rent(rent_id, arrears):
#     rent = Rent.query.get(rent_id)
#  this fn now gone!  last_rent_date = db.session.execute(func.mjinn.next_rent_date(rent.id, 1, 1)).scalar()
#     rent.lastrentdate = last_rent_date
#     rent.arrears = arrears


# def update_roll_rents(rent_prs):
#     update_vals = []
#     for rent_prop in rent_prs:
#         update_vals.append(update_roll_rent(rent_prop.id))
#     db.session.bulk_update_mappings(Rent, update_vals)
