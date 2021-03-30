import datetime
from app import app, init_app, db
from app.models import User


# Call `init_app()` in `__init__.py` here
# We declare and create the global `app` instance in `__init__.py`
# This allows us to access it, and use function decorations like `@app.context_processor`, from other modules
# which would not be the case if we created `app` from this module
init_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


@app.context_processor
def inject_today_date():
    return {'today_date': datetime.date.today()}


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)
