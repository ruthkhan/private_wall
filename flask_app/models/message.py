from flask import session, flash
from datetime import datetime
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user

class Message: # change class object name

    db = 'private_wall' # change DB

    def __init__(self, data): # check against values in ERD
        self.id = data['id']
        self.content = data['content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.sender_id = data['sender_id']
        self.recipient_id = data['recipient_id']
        self.sender = data['sender']
        self.time_since = data['time_since']
    
    @classmethod
    def save_message(cls, data): # add new message
        query = """
            INSERT INTO messages(content, created_at, updated_at, sender_id, recipient_id)
            VALUES(%(content)s, NOW(), NOW(), %(sender_id)s, %(recipient_id)s);
            """
        result = connectToMySQL(cls.db).query_db(query, data) # returns id no of new message
        return result 
    
    @classmethod
    def delete(cls, id): # delete an existing message
        query = """
            DELETE FROM messages
            WHERE id = %(id)s;
            """
        connectToMySQL(cls.db).query_db(query, {'id':id})
    
    @staticmethod
    def validate_message(data): # validate for both new and update rides
        is_valid = True
        if len(data['content'].strip()) < 5: 
            is_valid = False 
            flash('Message must be at least 5 characters.', 'add')
        return is_valid
    
    @staticmethod 
    def time_calculate(data): 
        time_since = (datetime.now() - data).total_seconds()
        if time_since < 60: 
            time_string = "Now"
        elif time_since < (60*60): 
            minutes = round(time_since/60)
            time_string = f"{minutes} minutes ago" 
        elif time_since < (60*60*24): 
            hours = round(time_since/(60*60))
            time_string = f"{hours} hours ago"
        elif time_since < (60*60*24*30): 
            days = round(time_since/(60*60*24))
            time_string = f"{days} days ago"
        elif time_since < (60*60*24*365): 
            months = round(time_since/(60*60*24*30))
            time_string = f"{months} months ago"
        else: 
            time_string = "A long time ago"
        return time_string