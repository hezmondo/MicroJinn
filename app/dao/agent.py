from sqlalchemy.orm import load_only
from app import db
from app.dao.database import commit_to_database
from app.models import Agent, Headrent, Rent


def get_agents_set(filter, list):
    agents = db.session.query(Agent).filter(*filter).all()
    # agents = sorted(agents, key=lambda o: list.index(o.id))

    return agents


def get_agent(agent_id):
    return db.session.query(Agent).filter_by(id=agent_id).one()


def get_agent_id(agent_detail):
    return db.session.query(Agent).filter_by(detail=agent_detail).first()


def get_agent_rents(agent_id, type='rent'):
    if agent_id and agent_id != 0:
        if type == 'rent':
            agent_rents = db.session.query(Rent).filter_by(agent_id=agent_id) \
                .options(load_only('id', 'rentcode', 'tenantname')).all()
        else:
            agent_rents = db.session.query(Headrent).filter_by(agent_id=agent_id) \
                .options(load_only('id', 'code', 'propaddr')).all()
    else:
        agent_rents = None

    return agent_rents


def post_agent(agent, agent_id, rent_id):
    try:
        db.session.add(agent)
        db.session.flush()
        message = "Agent details updated successfully!"
        agent_id = agent.id
        if rent_id != 0:
            rent = Rent.query.get(rent_id)
            rent.agent_id = agent_id
            rent.mailto_id = 1
            db.session.add(Rent)
            message += " Please review this rent\'s mailto details."
        commit_to_database()
    except Exception as ex:
        message = f"Update agent failed. Error:  {str(ex)}"

    return agent_id, message
