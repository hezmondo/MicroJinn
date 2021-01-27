from app import db
from flask import request
from app.dao.common import get_idlist_recent, pop_idlist_recent
from app.dao.functions import commit_to_database
from app.models import Agent, Headrent, Rent


def delete_agent(agent_id):
    Agent.query.filter_by(id=agent_id).delete()
    commit_to_database()


def get_agents():
    if request.method == "POST":
        detail = request.form.get("detail") or ""
        email = request.form.get("email") or ""
        note = request.form.get("note") or ""
        agents = Agent.query.filter(Agent.detail.ilike('%{}%'.format(detail)),
                    Agent.email.ilike('%{}%'.format(email)), Agent.note.ilike('%{}%'.format(note))).all()
    else:
        id_list = get_idlist_recent("recent_agents")
        agents = Agent.query.filter(Agent.id.in_(id_list))

    return agents


def get_agent(agent_id):
    agent = Agent.query.get(agent_id)
    pop_idlist_recent("recent_agents", agent_id)

    return agent


def get_agent_rents(agent_id):
    agent_rents = Agent.query.join(Rent).with_entities(Rent.id, Rent.rentcode, Rent.tenantname) \
        .filter(Rent.agent_id == agent_id) \
        .all()

    agent_headrents = Agent.query.join(Headrent).with_entities(Headrent.id, Headrent.code, Headrent.propaddr) \
        .filter(Headrent.agent_id == agent_id) \
        .all()

    return agent_headrents, agent_rents


def post_agent(agent_id):
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
    _id = agent.id
    commit_to_database()

    return _id
