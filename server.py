from flask import Flask, request, jsonify
from models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitor.db'

db.init_app(app)

@app.route('/withdrawal', methods=['POST'])
def withdrawal():
    data = request.get_json()
    return jsonify(src=data['src'], dest=data['dest'], amount=data['amount'])



