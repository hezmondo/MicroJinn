from app import app, db
from app.models import User, Rent


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Rent': Rent}


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)
