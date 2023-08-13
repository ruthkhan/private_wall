from flask import session, flash
from flask_bcrypt import Bcrypt
import re 
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import message

bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User: 

    db = 'private_wall' # change DB path

    def __init__(self, data): # initialise object - match against ERD fields
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.messages = []
        self.messages_sent = 0
        self.messages_received = 0

    @classmethod
    def save_user(cls, data): # insert user into DB; hash password first
        data_dict = dict(data)
        data_dict['password'] = bcrypt.generate_password_hash(data['password'])
        query = """
            INSERT INTO users (first_name, last_name, email, password, created_at, updated_at)
            VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW());
            """
        result = connectToMySQL(cls.db).query_db(query, data_dict)
        return result # returns user id

    @classmethod
    def get_all(cls, id): # get all users except myself
        query = """
            SELECT * FROM users
            WHERE id != %(id)s
            ORDER BY first_name ASC;
            """
        results = connectToMySQL(cls.db).query_db(query, {'id': id})
        all_users = []
        for i in results: 
            all_users.append(cls(i))
        return all_users

    @classmethod
    def get_user(cls, id): # get user by id 
        query = """
            SELECT * FROM users
            WHERE id = %(id)s;
            """
        result = connectToMySQL(cls.db).query_db(query, {'id': id})
        return cls(result[0])

    @classmethod
    def get_userid(cls, data): # get user by email usually for login
        query = """
            SELECT id FROM users
            WHERE email = %(email)s;
            """
        result = connectToMySQL(cls.db).query_db(query, data)
        return result[0]['id'] #returns userid
    
    @classmethod
    def get_user_messages(cls, id): # get all messages for one recipient
        query = """
            SELECT * FROM users
            LEFT JOIN messages ON messages.recipient_id = users.id
            WHERE users.id = %(id)s
            ORDER BY messages.updated_at DESC;
            """
        results = connectToMySQL(cls.db).query_db(query, {'id':id})
        this_user = cls(results[0])
        this_user.messages_received = 0
        for i in results: 
            if i['messages.id']:
                message_data = {
                    'id': i['messages.id'], 
                    'content': i['content'],
                    'created_at': i['messages.created_at'], 
                    'updated_at': i['messages.updated_at'], 
                    'sender_id': i['sender_id'],
                    'recipient_id': i['recipient_id'],
                    'sender': cls.get_user(i['sender_id']),
                    'time_since': message.Message.time_calculate(i['messages.updated_at'])
                }
                this_user.messages.append(message.Message(message_data))
                this_user.messages_received +=1
        this_user.messages_sent = User.sent_count(id)
        return this_user

    @staticmethod
    def valid_reg(data): # validate registration
        is_valid = True
        if len(data['first_name'].strip()) < 2: 
            is_valid = False
            flash('First name must be at least 2 characters', 'register')
        if len(data['last_name'].strip()) < 2: 
            is_valid = False
            flash('Last name must be at least 2 characters', 'register')
        if not EMAIL_REGEX.match(data['email']): 
            is_valid = False
            flash('Invalid email format', 'register')
        if len(data['password'].strip()) < 8: 
            is_valid = False
            flash('Password must be at least 8 characters', 'register')
        if data['password'] != data['confirm_pw']: 
            is_valid = False
            flash('Password and Confirm PW do not match', 'register')
        #check if user exists in DB
        query = """
            SELECT * FROM users
            WHERE email = %(email)s; 
            """
        result = connectToMySQL(User.db).query_db(query, data)
        if len(result)>0: 
            is_valid = False
            flash('This email has already been registered', 'register')
        return is_valid
    
    @staticmethod
    def valid_login(data): # validate login email only; pw check done in controller
        is_valid = True 
        # check if user exists in DB
        query = """
            SELECT password FROM users
            WHERE email = %(email)s; 
            """
        result = connectToMySQL(User.db).query_db(query, data)
        if not result: 
            is_valid = False
            flash('Invalid email/password', 'login')
        elif not bcrypt.check_password_hash(result[0]['password'], data['password']): # check password if user exists
            is_valid = False
            flash('Invalid email/password', 'login')
        return is_valid
    
    @staticmethod
    def sent_count(id): # count messages sent by user 
        query = """
            SELECT COUNT(*) AS count FROM messages 
            WHERE sender_id = %(id)s;
            """
        result = connectToMySQL(User.db).query_db(query, {'id': id})
        return result[0]['count']