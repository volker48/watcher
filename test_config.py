import tempfile

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + tempfile.NamedTemporaryFile().name