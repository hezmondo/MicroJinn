from app import db
from flask import request
from app.main.common import get_idlist_recent, pop_idlist_recent
from app.main.functions import commit_to_database
from app.models import Agent


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


def get_agent(id):
    if request.method == "POST":
        id = post_agent(id)
    if id != 0:
        agent = Agent.query.get(id)
        pop_idlist_recent("recent_agents", id)
    else:
        agent = Agent()
        agent.id = 0

    return agent


def post_agent(id):
    agent = Agent.query.get(id) or Agent()
    agent.detail = request.form.get("detail")
    agent.email = request.form.get("email")
    agent.note = request.form.get("note")
    db.session.add(agent)
    db.session.flush()
    _id = agent.id
    commit_to_database()

    return _id
