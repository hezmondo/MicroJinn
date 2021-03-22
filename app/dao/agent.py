from sqlalchemy.orm import load_only
from app import db
from app.dao.database import commit_to_database, pop_idlist_recent
from app.models import Agent, Headrent, Rent


def get_agents_set(filter):
    return db.session.query(Agent).filter(*filter).all()


def get_agent(agent_id):
    return db.session.query(Agent).filter_by(id=agent_id).one_or_none()


def get_agent_id(agent_detail):
    return db.session.query(Agent).filter_by(detail=agent_detail).first()


def get_agent_rents(agent_id):
    return db.session.query(Rent).filter_by(agent_id=agent_id).options(load_only('id', 'rentcode', 'tenantname')).all()


def get_agent_headrents(agent_id):
    return db.session.query(Headrent).filter_by(agent_id=agent_id).options(load_only('id', 'code', 'propaddr')).all()


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
            db.session.add(rent)
            message += " Mail has been set to agent. Please review this rent\'s mailto details."
        commit_to_database()
        # update the user recent_agents to include a newly created agent (after we have done the main database work)
        pop_idlist_recent("recent_agents", agent_id)
    except Exception as ex:
        message = f"Update agent failed. Error:  {str(ex)}"

    return agent_id, message
