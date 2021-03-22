from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.agent import get_agent, get_agent_rents, get_agent_headrents
from app.dao.common import delete_record
from app.dao.database import pop_idlist_recent
from app.dao.rent import post_rent_agent_unlink, post_rent_agent_update
from app.main.agent import get_agents, update_agent

agent_bp = Blueprint('agent_bp', __name__)


# TODO: move agent routes into views/agent, then simply routes so that the heavy lifting occurs in main/agent
@agent_bp.route('/agent/<int:agent_id>', methods=["GET", "POST"])
@login_required
def agent(agent_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    rentcode = request.args.get('rentcode', "ABC1", type=str)
    action = request.args.get('action', type=str)
    rents = None
    headrents = None
    if request.method == "POST":
        agent_id, message = update_agent(agent_id, rent_id)
        if rent_id != 0:
            return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))
    if agent_id == 0:
        agent = {"id": 0, "detail": "", "email": "", "note": "", "code": ""}
    else:
        # update the user recent_agents before we do the main database work
        pop_idlist_recent("recent_agents", agent_id)
        agent = get_agent(agent_id)
        rents = get_agent_rents(agent_id)
        headrents = get_agent_headrents(agent_id)
    return render_template('agent.html', action=action, agent=agent, rent_id=rent_id, rentcode=rentcode,
                           rents=rents, headrents=headrents)


@agent_bp.route('/agent_delete/<int:agent_id>', methods=["GET", "POST"])
@login_required
def agent_delete(agent_id):
    if request.method == "POST":
        rent_id = request.args.get('rent_id', 0, type=int)
        message = ""
        try:
            if rent_id != 0:
                post_rent_agent_unlink(rent_id)
                message = "This rent no longer has a agent. Mail has been set to tenant name at the property. "
            delete_record(agent_id, 'agent')
            message += "The agent has been deleted. "
        except Exception as ex:
            message = f"Error deleting agent: {str(ex)}"
        if rent_id == 0:
            return redirect(url_for('agent_bp.agents'))
        else:
            return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))


# TODO: Remove agent_rents route
@agent_bp.route('/agent_rents/<int:agent_id>', methods=["GET"])
@login_required
def agent_rents(agent_id):
    type = request.args.get('type', "rent", type=str)
    agent = get_agent(agent_id)
    agent_rents = get_agent_rents(agent_id)
    return render_template('agent_rents.html', agent=agent, agent_rents=agent_rents, type=type)


@agent_bp.route('/agent_unlink/<int:rent_id>', methods=["GET", "POST"])
@login_required
def agent_unlink(rent_id):
    if request.method == "POST":
        try:
            post_rent_agent_unlink(rent_id)
            message = "This rent no longer has a agent. Mail has been set to tenant name at the property. "
        except Exception as ex:
            message = f"Error deleting agent: {str(ex)}"
        return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))


@agent_bp.route('/agents', methods=['GET', 'POST'])
@login_required
def agents():
    rent_id = int(request.args.get('rent_id', "0", type=str))
    rentcode = request.args.get('rentcode', "ABC1", type=str)
    agent_id = request.args.get('agent_id', 0, type=int)
    agents, list = get_agents()
    if request.method == 'GET':
        agents = sorted(agents, key=lambda o: list.index(o.id))
    return render_template('agents.html', agents=agents, agent_id=agent_id, rent_id=rent_id, rentcode=rentcode)


@agent_bp.route('/agents_select', methods=['GET', 'POST'])
@login_required
def agents_select():
    rent_id = request.args.get('rent_id', type=int)
    agent_id = request.args.get('agent_id', type=int)
    # TODO: refactor message from post_rent_agent
    try:
        post_rent_agent_update(agent_id, rent_id)
        message = "Success! This rent has been linked to a new agent. Mail is set to agent. " \
                  "Please review the rent\'s mail address."
    except Exception as ex:
        message = f'Unable to update rent. Database write failed with error: {str(ex)}'
    return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))
