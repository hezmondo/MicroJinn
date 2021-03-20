from flask import request
from app.dao.common import get_idlist_recent
from app.dao.agent import get_agent, get_agents_set, post_agent
from app.models import Agent


def get_agents():
    filter = []
    list = []
    if request.method == "POST":    # get search parameters to create a filter
        detail = request.form.get("detail") or ""
        email = request.form.get("email") or ""
        note = request.form.get("note") or ""
        filter =[]
        if detail != "":
            filter.append(Agent.detail.ilike('%{}%'.format(detail)))
        if email != "":
            filter.append(Agent.email.ilike('%{}%'.format(email)))
        if note != "":
            filter.append(Agent.note.ilike('%{}%'.format(note)))
    else:
        list = get_idlist_recent("recent_agents")
        filter.append(Agent.id.in_(list))
    agents = get_agents_set(filter)

    return agents, list


def update_agent(agent_id, rent_id):
    if agent_id == 0:
        agent = Agent()
    else:
        agent = get_agent(agent_id)
    agent.detail = request.form.get("detail")
    agent.email = request.form.get("email")
    agent.note = request.form.get("note")
    agent.code = request.form.get("code")
    agent_id, message = post_agent(agent, agent_id, rent_id)

    return agent_id, message
