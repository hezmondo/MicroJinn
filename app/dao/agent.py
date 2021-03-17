from app import db
from flask import request
from app.main.common import get_idlist_recent
from app.dao.database import commit_to_database, pop_idlist_recent
from app.models import Agent, Headrent, Rent


def get_agents():
    if request.method == "POST":
        detail = request.form.get("detail") or ""
        email = request.form.get("email") or ""
        note = request.form.get("note") or ""
        agents = Agent.query.filter(Agent.detail.ilike('%{}%'.format(detail)),
                    Agent.email.ilike('%{}%'.format(email)), Agent.note.ilike('%{}%'.format(note))).all()
    else:
        id_list = get_idlist_recent("recent_agents")
        agents = Agent.query.filter(Agent.id.in_(id_list)).all()
        agents = sorted(agents, key=lambda o: id_list.index(o.id))

    return agents


def get_agent(agent_id):
    return db.session.query(Agent).filter_by(id=agent_id).one()


def get_agent_id(agent_detail):
    return db.session.query(Agent).filter_by(detail=agent_detail).one()

def get_agent_rents(agent_id, type='rent'):
    if agent_id and agent_id != 0:
        if type == 'rent':
            agent_rents = Agent.query.join(Rent).with_entities(Rent.id, Rent.rentcode, Rent.tenantname) \
                .filter(Rent.agent_id == agent_id) \
                .all()
        else:
            agent_rents = Agent.query.join(Headrent).with_entities(Headrent.id, Headrent.code, Headrent.propaddr) \
                .filter(Headrent.agent_id == agent_id) \
                .all()
    else:
        agent_rents = None

    return agent_rents


def post_agent(agent_id, rent_id):
    try:
        if agent_id == 0:
            agent = Agent()
        else:
            agent = Agent.query.get(agent_id)
        agent.detail = request.form.get("detail")
        agent.email = request.form.get("email")
        agent.note = request.form.get("note")
        agent.code = request.form.get("code")
        db.session.add(agent)
        db.session.flush()
        message = "Agent details updated successfully!"
        agent_id = agent.id
        if rent_id != 0:
            rent = Rent.query.get(rent_id)
            rent.agent_id = agent_id
            message += " Please review this rent\'s mailto details."
        commit_to_database()
    except Exception as ex:
        message = f"Update agent failed. Error:  {str(ex)}"

    return agent_id, message
