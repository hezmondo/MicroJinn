from app.models import Manager_external, Rent_external


def get_rent_external(id):
    rent_external = Rent_external.query.join(Manager_external).with_entities(Rent_external.rentcode,
                     Rent_external.propaddr, Rent_external.tenantname, Rent_external.owner, Rent_external.rentpa,
                     Rent_external.arrears, Rent_external.lastrentdate, Rent_external.source, Rent_external.status,
                     Manager_external.codename, Manager_external.details, Rent_external.agentdetails) \
        .filter(Rent_external.id == id).one_or_none()

    return rent_external
