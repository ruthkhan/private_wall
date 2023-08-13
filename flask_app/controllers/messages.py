from flask import redirect, request
from flask_app import app
from flask_app.models import message

@app.route('/send', methods=["POST"])
def send_message(): 
    is_valid = message.Message.validate_message(request.form)
    if is_valid: 
        message.Message.save_message(request.form)
    return redirect('/wall')

@app.route('/delete/<int:id>')
def del_message(id): 
    message.Message.delete(id)
    return redirect('/wall')