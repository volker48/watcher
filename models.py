from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Checkpoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(64), primary_key=True)


class Address(db.Model):
    address = db.Column(db.String(34), primary_key=True)
    # Store the balance as an integer in Satoshis
    balance = db.Column(db.Integer)


class Transaction(db.Model):
    txid = db.Column(db.String(64), primary_key=True)


class Block(db.Model):
    hash = db.Column(db.String(64), primary_key=True)
    confirmations = db.Column(db.Integer)
    stripped_size = db.Column(db.Integer)
    size = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    version = db.Column(db.Integer)
    version_hex = db.Column(db.String(8))
    merkle_root = db.Column(db.String(64))
