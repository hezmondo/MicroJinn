from sqlalchemy import desc
from app.models import Income, IncomeAlloc, Landlord, Manager, MoneyAcc, Rent, TypePayment


def getmaildata(rent_id, income_id=0):
    if income_id == 0:
        incomedata = Income.query. \
            join(IncomeAlloc) \
            .join(TypePayment) \
            .with_entities(Income.id, Income.payer, Income.date.label("paydate"), Income.amount.label("payamount"),
                           TypePayment.paytypedet) \
            .filter(IncomeAlloc.rent_id == rent_id).order_by(desc(Income.date)).limit(1).one_or_none()
        # income_id = incomedata.id
    else:
        incomedata = Income.query \
            .join(IncomeAlloc) \
            .join(TypePayment) \
            .with_entities(Income.id, Income.payer, Income.date.label("paydate"), Income.amount.label("payamount"),
                           TypePayment.paytypedet) \
            .filter(Income.id == income_id).first()
    # allocdata = IncomeAlloc.join(ChargeType).with_entities(IncomeAlloc.id, IncomeAlloc.income_id,
    #                     IncomeAlloc.rentcode, IncomeAlloc.amount.label("alloctot"),
    #                     ChargeType.chargedesc).filter(IncomeAlloc.income_id == income_id).all()
    allocdata = None
    bankdata = MoneyAcc.query \
        .join(Landlord) \
        .join(Rent) \
        .with_entities(MoneyAcc.acc_name, MoneyAcc.acc_num, MoneyAcc.sort_code,
                       MoneyAcc.bank_name) \
        .filter(Rent.id == rent_id) \
        .one_or_none()
    addressdata = Landlord.query. \
        join(Rent) \
        .join(Manager) \
        .with_entities(Landlord.name, Landlord.address, Manager.manageraddr, Manager.manageraddr2) \
        .filter(Rent.id == rent_id).one_or_none()
    return incomedata, allocdata, bankdata, addressdata

