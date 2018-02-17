from flask import request, jsonify

from app import create_app

app = create_app()


@app.route('/withdrawal', methods=['POST'])
def withdrawal():
    data = request.get_json()
    return jsonify(src=data['src'], dest=data['dest'], amount=data['amount'])
