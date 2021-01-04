from app import db
from flask import request
from app.main.common import get_idlist_recent, pop_idlist_recent
from app.main.functions import commit_to_database
from app.models import Agent


def get_agents():
    if request.method == "POST":
        agd = request.form.get("address") or ""
        age = request.form.get("email") or ""
        agn = request.form.get("notes") or ""
        agents = Agent.query.filter(Agent.agdetails.ilike('%{}%'.format(agd)), Agent.agemail.ilike('%{}%'.format(age)),
                        Agent.agnotes.ilike('%{}%'.format(agn))).all()
    else:
        id_list = get_idlist_recent("recent_agents")
        agents = Agent.query.filter(Agent.id.in_(id_list))
    return agents


def get_agent(id):
    if id == 0:
        agent = Agent()
        agent.id = 0
    else:
        agent = Agent.query.get(id)
        pop_idlist_recent("recent_agents", id)
    if request.method == "POST":
        agent = post_agent(agent)

    return agent


def post_agent(agent):
    agdet = request.form.get("address")
    agent.agdetails = agdet
    agent.agemail = request.form.get("email")
    agent.agnotes = request.form.get("notes")
    db.session.add(agent)
    commit_to_database()
    agent = Agent.query.filter(Agent.agdetails == agdet).first()

    return agent
