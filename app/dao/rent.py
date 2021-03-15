import json
from decimal import Decimal
from app import db
from flask import flash, redirect, url_for, request
from sqlalchemy.orm import joinedload, load_only
from app.main.common import get_postvals_id, inc_date_m
from app.dao.database import pop_idlist_recent
from app.main.functions import strToDec
from app.models import Agent, Jstore, ManagerExt, PrHistory, Property, Rent, RentExternal
from app.dao.database import commit_to_database


def check_pr_exists(rent_id):   # check if rent has record in pr_history
    prhis = PrHistory.query.filter_by(rent_id=rent_id).first()
    return 1 if prhis and len(prhis) >= 1 else 0


def create_new_rent():
    # create new rent and property function not yet built, so return id for dummy rent:
    return 23


def get_mailaddr(rent_id, agent_id, mailto_id, tenantname):
    if agent_id and agent_id != 0 and mailto_id in (1, 2):
        # agent = db.session.query(Agent) \
        #     .filter_by(id=agent_id).options(load_only('detail')).one()
        agent = Agent.query.filter_by(id=agent_id).first()
        mailaddr = agent.detail
        if mailto_id == 2:
            mailaddr = tenantname + 'care of' + mailaddr
    else:
        propaddr = get_propaddr(rent_id)
        if mailto_id == 4:
            mailaddr = 'the owner or occupier' + propaddr
        else:
            mailaddr = tenantname +', ' + propaddr

    return mailaddr


def get_propaddr(rent_id):
    # p_addrs = db.session.query(Property) \
    #     .filter_by(rent_id=rent_id).options(load_only('propaddr')).all()
    p_addrs = Property.query.filter_by(rent_id=rent_id).all()
    p_addr = '; '.join(each.propaddr.strip() for each in p_addrs)
    return p_addr


def get_rent(rent_id):  #returns all Rent member variables as a mutable dict
    if rent_id == 0:
        # take the user to create new rent function:
        rent_id = create_new_rent()
    rent = Rent.query.filter_by(id=rent_id).first()
    if rent is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))
    else:
        pop_idlist_recent("recent_rents", rent_id)

    return rent


def get_rent_md(rent_id):   #returns 5 Rent member variables as a mutable dict for mail_dialog
    return db.session.query(Rent).filter_by(id=rent_id).options(load_only('id', 'agent_id', 'datecode_id',
                                                                  'mailto_id', 'rentcode', 'tenantname')) \
        .one_or_none()


def get_rent_x(rent_id):    #returns all non Rent (joined) member variables for rent screen, mail, payrequest
    return db.session.query(Rent) \
        .filter_by(id=rent_id).options(joinedload('agent').load_only('id', 'detail'),
                                    joinedload('landlord').options(load_only('name'),
                                    joinedload('manager').load_only('managername', 'manageraddr'),
                                    joinedload('money_account').load_only('acc_name', 'acc_num', 'bank_name', 'sort_code')),
                                    joinedload('typeactype').load_only('actypedet'),
                                    joinedload('typeadvarr').load_only('advarrdet'),
                                    joinedload('typedeed').load_only('deedcode', 'info'),
                                    joinedload('typefreq').load_only('freqdet'),
                                    joinedload('typemailto').load_only('mailtodet'),
                                    joinedload('typeprdelivery').load_only('prdeliverydet'),
                                    joinedload('typesalegrade').load_only('salegradedet'),
                                    joinedload('typestatus').load_only('statusdet'),
                                    joinedload('typetenure').load_only('tenuredet')) \
        .one_or_none()


def get_rent_external(id):
    rent_external = RentExternal.query \
        .join(ManagerExt) \
        .with_entities(RentExternal.rentcode, RentExternal.propaddr, RentExternal.tenantname, RentExternal.owner, RentExternal.rentpa,
                       RentExternal.arrears, RentExternal.lastrentdate, RentExternal.source, RentExternal.status,
                       ManagerExt.codename, ManagerExt.detail, RentExternal.agentdetail) \
        .filter(RentExternal.id == id).one_or_none()
    return rent_external


def get_rent_sdata(qfilter, action, runsize):
    if action == "basic":
        # # simple search of views rents submitted from home page
        rent_s = db.session.query(Rent) \
            .options(load_only('id', 'rentcode', 'arrears', 'datecode_id', 'freq_id', 'lastrentdate',
                               'rentpa', 'source', 'tenantname'),
                joinedload('agent').load_only('detail'),
                joinedload('typestatus').load_only('statusdet'),
                joinedload('typetenure').load_only('tenuredet')) \
            .filter(*qfilter).order_by(Rent.rentcode).limit(runsize).all()
    elif action == "external":
        # simple search of external rents submitted from home page - not yet completed
        rent_s = db.session.query(RentExternal) \
            .options(load_only('id', 'agentdetail', 'arrears', 'datecode_id', 'lastrentdate', 'rentcode', 'owner',
                               'propaddr', 'rentpa', 'source', 'status', 'tenantname'),
                joinedload('manager_external').load_only('codename')) \
            .filter(*qfilter).order_by(RentExternal.rentcode).limit(runsize).all()
    else:
        # advanced search submitted from filter page
        rent_s = db.session.query(Rent) \
            .options(load_only('id', 'rentcode', 'arrears', 'datecode_id', 'email', 'freq_id', 'lastrentdate', 'note',
                               'price', 'rentpa', 'source', 'tenantname'),
                joinedload('agent').load_only('detail'),
                joinedload('landlord').load_only('name'),
                joinedload('typeactype').load_only('actypedet'),
                joinedload('typeadvarr').load_only('advarrdet'),
                joinedload('typeprdelivery').load_only('prdeliverydet'),
                joinedload('typesalegrade').load_only('salegradedet'),
                joinedload('typestatus').load_only('statusdet'),
                joinedload('typetenure').load_only('tenuredet')) \
            .filter(*qfilter).order_by(Rent.rentcode).limit(runsize).all()
    return rent_s


def post_rent_agent(agent_id, rent_id):
    message = ""
    try:
        if rent_id != 0:
            rent = Rent.query.get(rent_id)
            if agent_id != 0:
                rent.agent_id = agent_id
                message = "Success! This rent has been linked to a new agent. Please review the rent\'s mail address."
            else:
                rent.agent_id = None
                message = "Success! This rent no longer has an agent."
                # change mailto from agent to tenant
                if rent.mailto_id == 1 or 2:
                    rent.mailto_id = 3
                    message += " The mail address has been set to tenant name at the property."
        commit_to_database()
    except Exception as ex:
        message = f"Update rent failed. Error:  {str(ex)}"
    return message


def post_rent__filter(filterdict):
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
    db.session.commit()


def post_rent(rent_id):
    rent = Rent.query.get(rent_id)
    postvals_id = get_postvals_id()
    # we need the post values with the class id generated for the actual combobox values:
    rent.actype_id = postvals_id["actype"]
    rent.advarr_id = postvals_id["advarr"]
    rent.arrears = strToDec(request.form.get("arrears"))
    # we need code to generate datecode_id from lastrentdate with user choosing sequence:
    rent.datecode_id = int(request.form.get("datecode_id"))
    rent.deed_id = postvals_id["deedcode"]
    rent.freq_id = postvals_id["frequency"]
    rent.landlord_id = postvals_id["landlord"]
    rent.lastrentdate = request.form.get("lastrentdate")
    price = request.form.get("price")
    rent.price = price if (price and price != 'None') else Decimal(99999)
    rent.rentpa = strToDec(request.form.get("rentpa"))
    rent.salegrade_id = postvals_id["salegrade"]
    rent.source = request.form.get("source")
    rent.status_id = postvals_id["status"]
    rent.tenure_id = postvals_id["tenure"]
    db.session.add(rent)
    db.session.flush()
    rent_id = rent.id
    db.session.commit()

    return rent_id


# def update_roll_rent(rent_id, arrears):
#     rent = Rent.query.get(rent_id)
#  this fn now gone!  last_rent_date = db.session.execute(func.mjinn.next_rent_date(rent.id, 1, 1)).scalar()
#     rent.lastrentdate = last_rent_date
#     rent.arrears = arrears


def update_roll_rent(rent_id, last_rent_date, arrears):
    rent = Rent.query.get(rent_id)
    rent.lastrentdate = last_rent_date
    rent.arrears = arrears


def update_rollback_rent(rent_id, arrears):
    rent = Rent.query.get(rent_id)
    last_rent_date = inc_date_m(rent.lastrentdate, rent.freq_id, rent.datecode_id, -1)
    rent.lastrentdate = last_rent_date
    rent.arrears = arrears


# def update_roll_rents(rent_prs):
#     update_vals = []
#     for rent_prop in rent_prs:
#         update_vals.append(update_roll_rent(rent_prop.id))
#     db.session.bulk_update_mappings(Rent, update_vals)


def update_tenant(rent_id):
    rent = Rent.query.get(rent_id)
    rent.tenantname = request.form.get("tenantname")
    postvals_id = get_postvals_id()
    rent.mailto_id = postvals_id["mailto"]
    rent.email = request.form.get("email")
    rent.prdelivery_id = postvals_id["prdelivery"]
    rent.note = request.form.get("note")
    db.session.add(rent)
    db.session.commit()

