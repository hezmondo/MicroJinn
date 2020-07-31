import datetime
from app import create_app, db
from app.models import User


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


@app.context_processor
def inject_today_date():
    return {'today_date': datetime.date.today().strftime('%d-%b-%Y')}


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)
