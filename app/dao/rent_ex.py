from app.models import ManagerExt, RentExt


def get_rent_ex(id):
    rent_ex = RentExt.query \
        .join(ManagerExt) \
        .with_entities(RentExt.rentcode, RentExt.propaddr, RentExt.tenantname, RentExt.owner, RentExt.rentpa,
                       RentExt.arrears, RentExt.lastrentdate, RentExt.source, RentExt.status,
                       ManagerExt.codename, ManagerExt.detail, RentExt.agentdetail) \
        .filter(RentExt.id == id).one_or_none()
    return rent_ex


