from sqlalchemy.orm import load_only
from app import db
from app.dao.common import pop_idlist_recent
from app.dao.database import commit_to_database
from app.models import Agent, Headrent, Rent


def add_agent(agent):
    db.session.add(agent)
    db.session.flush()
    return agent.id


def get_agents_set(filter):
    return db.session.query(Agent).filter(*filter).all()


def get_agent(agent_id):
    return db.session.query(Agent).filter_by(id=agent_id).one_or_none()


def get_agent_id(agent_detail):
    return db.session.query(Agent).filter_by(detail=agent_detail).first()
