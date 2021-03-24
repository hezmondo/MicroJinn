from flask import request
from app.dao.common import delete_record, get_idlist_recent, pop_idlist_recent
from app.dao.agent import add_agent, get_agent, get_agents_set
from app.dao.database import commit_to_database
from app.dao.headrent import get_agent_headrents, get_headrent_row
from app.dao.rent import get_agent_rents, get_rent_row
from app.models import Agent


def get_agents():
    filter = []
    list = []
    if request.method == "POST":    # unpack search parameters to create a filter
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


def delete_agent(agent_id, rent_id=0):
    message = ""
    try:
        if rent_id != 0:
            set_rent_agent_unlink(rent_id)
            message = "This rent no longer has a agent. Mail has been set to tenant name at the property. "
        delete_record(agent_id, 'agent')
        message += "The agent has been deleted. "
    except Exception as ex:
        message = f"Error deleting agent: {str(ex)}"
    return message


def delete_agent_headrent(agent_id, headrent_id=0):
    message = ""
    try:
        if headrent_id != 0:
            set_headrent_agent_unlink(headrent_id)
            message = "This headrent no longer has a agent. "
        delete_record(agent_id, 'agent')
        message += "The agent has been deleted. "
    except Exception as ex:
        message = f"Error deleting agent: {str(ex)}"
    return message


def populate_agent_from_form(agent):
    agent.detail = request.form.get("detail")
    agent.email = request.form.get("email")
    agent.note = request.form.get("note")
    agent.code = request.form.get("code")
    return agent


def prepare_agent_template(agent_id):
    rents = None
    headrents = None
    if agent_id == 0:
        agent = {"id": 0, "detail": "", "email": "", "note": "", "code": ""}
    else:
        # update the user recent_agents before we do the main database work
        pop_idlist_recent("recent_agents", agent_id)
        agent = get_agent(agent_id)
        rents = get_agent_rents(agent_id)
        headrents = get_agent_headrents(agent_id)
    return agent, rents, headrents


def select_new_agent(agent_id, rent_id):
    try:
        set_rent_agent(agent_id, rent_id)
        commit_to_database()
        message = "Success! This rent has been linked to a new agent. Mail is set to agent. " \
                  "Please review the rent\'s mail address."
    except Exception as ex:
        message = f'Unable to update rent. Database write failed with error: {str(ex)}'
    return message


def set_headrent_agent_unlink(headrent_id):
    headrent = get_headrent_row(headrent_id)
    headrent.agent_id = None


def set_rent_agent_unlink(rent_id):
    rent = get_rent_row(rent_id)
    rent.agent_id = None
    # change mailto to tenant
    if rent.mailto_id == 1 or 2:
        rent.mailto_id = 3


def set_rent_agent(agent_id, rent_id):
    rent = get_rent_row(rent_id)
    rent.agent_id = agent_id
    # change mailto to agent
    rent.mailto_id = 1


def update_agent(agent_id, rent_id=0):
    try:
        agent = Agent() if agent_id == 0 else get_agent(agent_id)
        agent = populate_agent_from_form(agent)
        agent_id = add_agent(agent)
        message = "Agent details updated successfully! "
        if rent_id != 0:
            set_rent_agent(agent_id, rent_id)
            message += "Mail has been set to agent. Please review this rent\'s mailto details."
        commit_to_database()
        # update the user recent_agents to include a newly created agent (after we have done the main database work)
        pop_idlist_recent("recent_agents", agent_id)
    except Exception as ex:
        message = f"Update agent failed. Error:  {str(ex)}"
    return agent_id, message


def unlink_agent_from_rent(rent_id):
    try:
        set_rent_agent_unlink(rent_id)
        commit_to_database()
        message = "This rent no longer has a agent. Mail has been set to tenant name at the property. "
    except Exception as ex:
        message = f"Error deleting agent: {str(ex)}"
    return message
