from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.agent import get_agent, get_agents, post_agent

ag_bp = Blueprint('ag_bp', __name__)

@ag_bp.route('/agents', methods=['GET', 'POST'])
def agents():
    agents = get_agents()

    return render_template('agents.html', agents=agents)

@ag_bp.route('/agent/<int:id>', methods=["GET", "POST"])
@login_required
def agent(id):
    if request.method == "POST":
        id = post_agent(id)
        return redirect(url_for('ag_bp.agent', id=id))
    agent = get_agent(id) if id != 0 else {"id": 0, "detail": "", "email": "", "note": "", "code": ""}

    return render_template('agent.html', agent=agent)


