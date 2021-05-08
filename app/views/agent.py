from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.main.agent import delete_agent, delete_agent_headrent, mget_agents_from_recent, mget_agents_from_search, \
    prepare_agent_template, select_new_agent, \
    update_agent, unlink_agent_from_rent

agent_bp = Blueprint('agent_bp', __name__)


@agent_bp.route('/agent/<int:agent_id>', methods=["GET", "POST"])
@login_required
# TODO: Refector so that we are not using '0' as a value for any ids.
def agent(agent_id):
    headrent_id = request.args.get('headrent_id', type=int)
    rent_id = request.args.get('rent_id', type=int)
    rentcode = request.args.get('rentcode', "ABC1", type=str)
    action = request.args.get('action', type=str)
    if request.method == "POST":
        agent_id, message = update_agent(agent_id, rent_id)
        if rent_id != 0:
            return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))
    agent, rents, headrents = prepare_agent_template(agent_id)
    return render_template('agent.html', action=action, agent=agent, headrent_id=headrent_id, rent_id=rent_id,
                           rentcode=rentcode, rents=rents, headrents=headrents)


@agent_bp.route('/agent_delete/<int:agent_id>', methods=["GET", "POST"])
@login_required
def agent_delete(agent_id):
    if request.method == "POST":
        rent_id = request.args.get('rent_id', 0, type=int)
        headrent_id = request.args.get('headrent_id', 0, type=int)
        message = delete_agent(agent_id, rent_id) if headrent_id == 0 else delete_agent_headrent(agent_id, headrent_id)
        if rent_id == 0:
            return redirect(url_for('agent_bp.agents'))
        else:
            return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))


@agent_bp.route('/agent_unlink/<int:rent_id>', methods=["GET", "POST"])
@login_required
def agent_unlink(rent_id):
    if request.method == "POST":
        message = unlink_agent_from_rent(rent_id)
        return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))


@agent_bp.route('/agents', methods=['GET', 'POST'])
@login_required
def agents():
    rent_id = request.args.get('rent_id', 0, type=int)
    rentcode = request.args.get('rentcode', "ABC1", type=str)
    agent_id = request.args.get('agent_id', 0, type=int)
    fdict = {}
    if request.method == 'POST':
        agents, fdict = mget_agents_from_search()
    else:
        agents = mget_agents_from_recent()
    return render_template('agents.html', agents=agents, agent_id=agent_id, fdict=fdict, rent_id=rent_id,
                           rentcode=rentcode)


@agent_bp.route('/agents_select', methods=['GET', 'POST'])
@login_required
def agents_select():
    rent_id = request.args.get('rent_id', type=int)
    agent_id = request.args.get('agent_id', type=int)
    message = select_new_agent(agent_id, rent_id)
    return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))
