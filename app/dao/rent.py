import json
from app import db
from flask import flash, redirect, url_for, request
from sqlalchemy import select
from sqlalchemy.orm import joinedload, load_only, contains_eager
from app.dao.common import pop_idlist_recent
from app.dao.database import commit_to_database
from app.models import Agent, Charge, Landlord, Jstore, Rent, RentExternal


def create_new_rent():
    # create new rent and property function not yet built, so return id for dummy rent:
    return 23


def dbget_rent_id(rentcode):
    return db.session.execute(select(Rent.id).where(Rent.rentcode==rentcode)).scalar().one


def delete_rent_filter(item_id):
    Jstore.query.filter_by(id=item_id).delete()
    commit_to_database()


def get_agent_rents(agent_id):
    return db.session.query(Rent).filter_by(agent_id=agent_id).options(load_only('id', 'rentcode', 'tenantname')).all()


def get_rent(rent_id):  # returns all Rent member variables plus associated items as a mutable dict
    if rent_id == 0:  # take the user to create new rent function (not yet built)
        rent_id = create_new_rent()
    pop_idlist_recent("recent_rents", rent_id)
    # rent = Rent.query.filter_by(id=rent_id).first()
    rent = db.session.query(Rent) \
        .filter_by(id=rent_id) \
        .options(joinedload('agent').load_only('id', 'detail'),
                 joinedload('landlord').options(load_only('name'),
                                                joinedload('manager').load_only('managername', 'manageraddr',
                                                                                'manageraddr2'),
                                                joinedload('money_account').load_only('acc_name', 'acc_num',
                                                                                      'bank_name', 'sort_code')),
                 joinedload('typedeed').load_only('deedcode', 'info')) \
        .one_or_none()
    if rent is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))

    return rent


def get_rentcode(rent_id):
    stmt = select(Rent.rentcode).filter_by(id=rent_id)
    return db.session.execute(stmt).scalar_one_or_none()


def get_rent_md(rent_id):  # returns 5 Rent member variables as a mutable dict for mail_dialog
    return db.session.query(Rent) \
        .filter_by(id=rent_id).options(load_only('id', 'agent_id', 'datecode_id',
                                                 'mailto_id', 'rentcode', 'tenantname')) \
        .one_or_none()


def get_rent_external(rent_id):
    return db.session.query(RentExternal) \
        .filter_by(id=rent_id).options(joinedload('manager_external').load_only('codename', 'detail')) \
        .one_or_none()


def get_rent_row(rent_id):
    return Rent.query.get(rent_id)


def getrents_basic_sql(sql):  # simple filtered rents for main rents page using raw sql
    return db.session.execute(sql).fetchall()


def getrents_advanced(filtr, runsize):
    stmt = select(Rent).join(Rent.prop_rent).join(Landlord).outerjoin(Agent).outerjoin(Rent.charge_rent) \
        .options(contains_eager(Rent.prop_rent).load_only('propaddr'),
                 load_only('advarr_id', 'arrears', 'freq_id', 'lastrentdate', 'prdelivery_id', 'rentcode',
                           'rentpa', 'source', 'tenantname', 'datecode_id'),
                 joinedload('agent').load_only('detail'))
    return db.session.execute(stmt.filter(*filtr).limit(runsize)).unique().scalars().all()


def get_rentsexternal(filtr):  # simple filtered external rents for main rents page or external rents page
    return db.session.query(RentExternal) \
        .options(load_only('id', 'agentdetail', 'arrears', 'datecode_id', 'lastrentdate', 'rentcode', 'owner',
                           'propaddr', 'rentpa', 'source', 'status', 'tenantname'),
                 joinedload('manager_external').load_only('codename')) \
        .filter(*filtr).order_by(RentExternal.rentcode).limit(30).all()


def get_rents_filters(typ):  # get stored advanced filter for advanced queries and payrequest pages
    filters = Jstore.query.filter(Jstore.type == typ).all()

    return filters


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
    jstore.description = request.form.get("filterdesc")
    jstore.content = json.dumps(filterdict)
    db.session.add(jstore)
    commit_to_database()


def post_rent(rent):
    db.session.add(rent)
    db.session.flush()
    rent_id = rent.id
    commit_to_database()

    return rent_id


def update_filter_last_used(code, datetime):
    jstore = db.session.execute(select(Jstore).filter_by(code=code)).scalar_one()
    jstore.last_used = datetime
    commit_to_database()
