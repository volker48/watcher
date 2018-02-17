from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

SATOSHI = 1e8


class Checkpoint(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(64), unique=True, nullable=False)


class Address(db.Model):
    address = db.Column(db.String(34), primary_key=True)
    # Store the balance as an integer in Satoshis
    balance = db.Column(db.Integer, default=0)

    def get_balance(self):
        """
        Get the current balance of this address
        :return: balance in BTC
        """
        return self.balance / SATOSHI

    @staticmethod
    def get_or_create(hash):
        address = Address.query.filter_by(address=hash).one_or_none()
        if address is None:
            address = Address(address=hash)
            db.session.add(address)
            db.session.commit()
        return address


class Watchlist(db.Model):
    address = db.Column(db.String(34), primary_key=True)

    @staticmethod
    def add(hash):
        addr = Watchlist(address=hash)
        db.session.add(addr)
        db.session.commit()
        return addr

    @staticmethod
    def is_on_watchlist(address):
        return Watchlist.query.filter_by(address=address).one_or_none() is not None
