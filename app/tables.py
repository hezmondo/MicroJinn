from flask_table import Table, Col
 
class Results(Table):
    id = Col('Id', show=False)
    rentcode = Col('Rentcode')
    note = Col('Note')
    email = Col('Email')
    tenantname = Col('Tenant name')
    rentpa = Col('Rent per annum')
    arrears = Col('Rent arrears')
    lastrentdate = Col('Last rent date')
    propaddr = Col('Property address')
    landlord = Col('Landlord')