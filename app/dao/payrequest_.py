import json
from app import db, decimal_default
from app.dao.functions import dateToStr, commit_to_database
from app.models import Case, Charge, ChargeType, FormLetter, Landlord, Manager, MoneyAcc, PrArrearsMatrix, \
                        PrHistory, Rent, TypeAdvArr, TypeFreq, TypePrDelivery, TypeTenure
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from flask import request
from sqlalchemy import func
from app.dao.doc_ import convert_html_to_pdf


def add_charge(rent_id, recovery_charge_amount, chargetype_id):
    today_string = dateToStr(date.today())
    charge_type = get_charge_type(chargetype_id)
    charge_details = "£{} {} added on {}".format(recovery_charge_amount, charge_type.capitalize(), today_string)
    new_charge = Charge(chargetype_id=chargetype_id, chargestartdate=date.today(),
                        chargetotal=recovery_charge_amount, chargedetail=charge_details,
                        chargebalance=recovery_charge_amount, rent_id=rent_id)
    db.session.add(new_charge)


def calculate_arrears(arrears, freq_id, rent_pa):
    return arrears + (rent_pa / freq_id)


def forward_rent(rent_id, from_batch=False):
    rent = Rent.query.get(rent_id)
    last_rent_date = db.session.execute(func.mjinn.next_rent_date(rent_id, 1, 1)).scalar()
    arrears = calculate_arrears(rent.arrears, rent.freq_id, rent.rentpa)
    if not from_batch:
        rent.lastrentdate = last_rent_date
        rent.arrears = arrears
    else:
        return dict(id=rent_id, lastrentdate=last_rent_date, arrears=arrears)


def forward_rents(rent_prs):
    update_vals = []
    for rent_prop in rent_prs:
        update_vals.append(forward_rent(rent_prop.id, True))
    db.session.bulk_update_mappings(Rent, update_vals)


def forward_rent_case_and_charges(pr_history, pr_save_data, rent_id):
    forward_rent(rent_id)
    new_charge_dict = pr_save_data.get("new_charge_dict")
    if len(new_charge_dict) > 0:
        add_charge(new_charge_dict.get("rent_id"), Decimal(new_charge_dict.get("charge_total")),
                   new_charge_dict.get("charge_type_id"))
    if pr_save_data.get("create_case"):
        merge_case(rent_id, pr_history.id)
    return pr_history.id


def get_charge_start_date(rent_id):
    return db.session.execute(func.mjinn.newest_charge(rent_id)).scalar()


def get_charge_type(chargetype_id):
    return db.session.query(ChargeType.chargedesc).filter_by(id=chargetype_id).scalar()


def get_email_form_by_code(code):
    email_form = FormLetter.query.filter(FormLetter.code == code).one_or_none()
    return email_form


def get_typeprdelivery(typeprdelivery_id=1):
    return db.session.query(TypePrDelivery.prdeliverydet).filter_by(id=typeprdelivery_id).scalar()


def get_typeprdelivery_id(prdeliverydet='email'):
    return db.session.query(TypePrDelivery.id).filter_by(prdeliverydet=prdeliverydet).scalar()


def get_pr_file(pr_id):
    pr_file = PrHistory.query.join(Rent).with_entities(PrHistory.id, PrHistory.summary, PrHistory.block,
                                                       PrHistory.date, Rent.rentcode,
                                                       Rent.id.label("rent_id")) \
        .filter(PrHistory.id == pr_id).one_or_none()
    return pr_file


def get_pr_history(rent_id):
    return PrHistory.query.filter_by(rent_id=rent_id)


def get_previous_pr_history_entry(pr_id):
    pr_history = PrHistory.query.get(pr_id)
    rent_id = pr_history.rent_id
    return pr_history, rent_id


def get_recovery_info(suffix):
    recovery_info = PrArrearsMatrix.query.with_entities(PrArrearsMatrix.arrears_clause,
                                                        PrArrearsMatrix.recovery_charge,
                                                        PrArrearsMatrix.create_case). \
        filter_by(suffix=suffix).one_or_none()
    arrears_clause = recovery_info.arrears_clause
    create_case = recovery_info.create_case
    recovery_charge = recovery_info.recovery_charge
    return arrears_clause, create_case, recovery_charge


def get_rent_charge_details(rent_id):
    qfilter = [Charge.rent_id == rent_id]
    charges = Charge.query.join(Rent).join(ChargeType).with_entities(Charge.id, Rent.rentcode, ChargeType.chargedesc,
                                                                     Charge.chargestartdate, Charge.chargetotal,
                                                                     Charge.chargedetail, Charge.chargebalance) \
        .filter(*qfilter).all()
    return charges


def get_rent_pr(rent_id):
    rent_pr = \
        Rent.query \
            .join(Landlord) \
            .join(Manager) \
            .join(MoneyAcc) \
            .join(TypeAdvArr) \
            .join(TypeFreq) \
            .join(TypeTenure) \
            .with_entities(Rent.id, Rent.rentcode, Rent.arrears, Rent.datecode, Rent.email, Rent.lastrentdate,
                           func.mjinn.check_pr_exists(Rent.id).label('prexists'),
                           # the following function takes id, renttype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                           func.mjinn.next_rent_date(Rent.id, 1, 2).label('nextrentdate_plus1'),
                           func.mjinn.next_rent_date(Rent.id, 1, 3).label('nextrentdate_plus2'),
                           func.mjinn.paid_to_date(Rent.id).label('paidtodate'),
                           func.mjinn.mail_addr(Rent.id, 0, 0).label('mailaddr'),
                           func.mjinn.prop_addr(Rent.id).label('propaddr'),
                           func.mjinn.tot_charges(Rent.id).label('totcharges'),
                           func.mjinn.last_arrears_level(Rent.id).label('lastarrearslevel'),
                           Rent.rentpa, Rent.tenantname, Rent.freq_id, Landlord.name,
                           Manager.managername, Manager.manageraddr, Manager.manageraddr2,
                           MoneyAcc.bank_name, MoneyAcc.acc_name, MoneyAcc.acc_num, MoneyAcc.sort_code,
                           TypeAdvArr.advarrdet, TypeFreq.freqdet, TypeTenure.tenuredet) \
            .filter(Rent.id == rent_id) \
            .one_or_none()
    return rent_pr


def merge_case(rent_id, pr_id):
    case = Case()
    case.id = rent_id
    case.case_details = "Automatically created by payrequest {} on {}".format(pr_id, dateToStr(date.today()))
    case.case_nad = date.today() + relativedelta(days=30)
    db.session.merge(case)


def post_new_payrequest(method):
    pr_save_data, pr_history, rent_id = prepare_new_pr_history_entry(method)
    prepare_block_entry(pr_history)
    db.session.add(pr_history)
    db.session.flush()
    pr_id = forward_rent_case_and_charges(pr_history, pr_save_data, rent_id)
    commit_to_database()
    return pr_id, pr_save_data, rent_id


def post_updated_payrequest(pr_id):
    pr_history, rent_id = get_previous_pr_history_entry(pr_id)
    prepare_block_entry(pr_history)
    commit_to_database()
    return rent_id


def prepare_new_pr_history_entry(method='email'):
    pr_save_data = json.loads(request.form.get('pr_save_data'))
    rent_id = request.args.get('rent_id', type=int)
    pr_history = PrHistory()
    pr_history.rent_id = rent_id
    mailaddr = request.form.get('pr_addr')
    pr_history.summary = pr_save_data.get('pr_code') + "-" + method + "-" + mailaddr[0:25]
    pr_history.date = date.today()
    pr_history.rent_date = datetime.strptime(pr_save_data.get("rent_date_string"), '%Y-%m-%d')
    pr_history.total_due = pr_save_data.get("tot_due")
    pr_history.arrears_level = pr_save_data.get("new_arrears_level")
    # TODO: We are not using the typeprdelivery table yet in any meaningful way
    #  - should we remove it and make delivery_method in pr_history a string column?
    pr_history.delivery_method = get_typeprdelivery_id(method)
    # TODO: Add pending / delivered functionality
    pr_history.delivered = True
    return pr_save_data, pr_history, rent_id


def prepare_block_entry(pr_history):
    pr_history.block = request.form.get('xinput').replace("£", "&pound;")
    convert_html_to_pdf(pr_history.block, 'pr.pdf')


def serialize_pr_save_data(pr_save_data):
    pr_save_data = json.dumps(pr_save_data, default=decimal_default)
    return pr_save_data
