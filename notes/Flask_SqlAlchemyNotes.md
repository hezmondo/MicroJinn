### What to do when your database is out of sync with your Flask models and migrations

The ideal solution is that you generate an initial migration for your db schema as it was the day you started tracking migrations with Flask-Migrate and Alembic.

Doing this is simple if you remember to do it at the time. Just create a separate empty database (leave your real db alone), configure your app to use the empty database, and then generate a migration. This migration will have the entire schema. Once you have that migration generated, get rid of the empty database and restore your configuration back to the real db.

If you already have additional migrations then it gets a little bit more complicated. You will have to go back to the version of your code where you want to generate the initial migration, then follow the above procedure to generate it. Finally, you will need to insert the initial migration in the migration list as the first one. Look at a few of the migration scripts to figure out how each migration references the previous one. A couple of small edits should get you up and running.

If this seems like too much work, then the other alternative is that you use 
`db.create_all()` to generate the database up to the latest migration, and then 
`./manage.py db stamp head` to tell Alembic that it should consider the database updated.

### Some examples of Classmethods in Flask models

You'll probably want to use a classmethod to accomplish this.

	class User(db.Model):
		__tablename__ = 'user'

		user_id = db.Column(db.Integer, primary_key=True)
		name = db.Column(db.String(30), nullable=False)
		created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))
		updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))

		def __init__(self, name):
			self.name = name

		@classmethod
		def create(cls, **kw):
			obj = cls(**kw)
			db.session.add(obj)
			db.session.commit()

This way you can use User.create(name="kumaran") to create a new user that will be committed to the database.
Better yet, it is a great idea to create a mixin for this method and others like it so that the functionality can be easily reused in your other models:

	class BaseMixin(object):
		@classmethod
		def create(cls, **kw):
			obj = cls(**kw)
			db.session.add(obj)
			db.session.commit()

You can then reuse this functionality in your models by using multiple inheritance, like so:

	class User(BaseMixin, db.Model):
		__tablename__ = 'user'

		user_id = db.Column(db.Integer, primary_key=True)
		name = db.Column(db.String(30), nullable=False)
		created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))
		updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))

		def __init__(self, name):
			self.name = name

### Comment on when to use each of @static and @class

@staticmethod function is nothing more than a function defined inside a class. It is callable without instantiating the class first. It’s definition is immutable via inheritance.

Python does not have to instantiate a bound-method for object.
It eases the readability of the code: seeing @staticmethod, we know that the method does not depend on the state of object itself;
@classmethod function also callable without instantiating the class, but its definition follows Sub class, not Parent class, via inheritance, can be overridden by subclass. That’s because the first argument for  @classmethod function must always be cls (class).

Factory methods, that are used to create an instance for a class using for example some sort of pre-processing.
Static methods calling static methods: if you split a static methods in several static methods, you shouldn't hard-code the class name but use class methods