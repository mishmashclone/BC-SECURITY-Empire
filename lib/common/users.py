import threading
import string
import random
import bcrypt
from . import helpers
import json
from pydispatch import dispatcher


class Users():
    def __init__(self, mainMenu):
        self.mainMenu = mainMenu

        self.conn = self.mainMenu.conn

        self.lock = threading.Lock()

        self.args = self.mainMenu.args

        self.users = {}

    def get_db_connection(self):
        """
        Returns a handle to the DB
        """
        self.mainMenu.conn.row_factory = None
        return self.mainMenu.conn

    def user_exists(self, uid):
        """
        Return whether a user exists or not
        """
        conn = self.get_db_connection()
        cur = conn.cursor()
        exists = cur.execute("SELECT 1 FROM users WHERE id = ? LIMIT 1", (uid,)).fetchone()
        if exists:
            return True

        return False

    def add_new_user(self, user_name, password):
        """
        Add new user to cache
        """
        last_logon = helpers.getutcnow()
        conn = self.get_db_connection()
        message = False

        try:
            self.lock.acquire()
            cur = conn.cursor()
            success = cur.execute("INSERT INTO users (username, password, last_logon_time, enabled, admin) VALUES (?,?,?,?,?)",
                        (user_name, self.get_hashed_password(password), last_logon, True, False))

            if success:
                # dispatch the event
                signal = json.dumps({
                    'print': True,
                    'message': "Added {} to Users".format(user_name)
                })
                dispatcher.send(signal, sender="Users")
                message = True
            else:
                message = False
        finally:
            cur.close()
            self.lock.release()

        return message

    def disable_user(self, uid, disable):
        """
        Disable user
        """
        conn = self.get_db_connection()

        try:
            self.lock.acquire()
            cur = conn.cursor()

            if not self.user_exists(uid):
                    message = False
            elif self.is_admin(uid):
                signal = json.dumps({
                    'print': True,
                    'message': "Cannot disable admin account"
                })
                message = False
            else:
                cur.execute("UPDATE users SET enabled = ? WHERE id = ?",
                            (not(disable), uid))
                signal = json.dumps({
                    'print': True,
                    'message': 'User {}'.format('disabled' if disable else 'enabled')
                })
                message = True
        finally:
            cur.close()
            self.lock.release()

        dispatcher.send(signal, sender="Users")
        return message

    def user_login(self, user_name, password):
        last_logon = helpers.getutcnow()
        conn = self.get_db_connection()

        try:
            self.lock.acquire()
            cur = conn.cursor()
            user = cur.execute("SELECT password from users WHERE username = ? AND enabled = 1 LIMIT 1", (user_name,)).fetchone()
            
            if user == None:
                return None
            
            if not self.check_password(password, user[0]):
                return None

            cur.execute("SELECT * FROM users WHERE username = ? LIMIT 1"
                        , (user_name,))
            user = cur.fetchone()

            token = self.refresh_api_token()
            cur.execute("UPDATE users SET last_logon_time = ?, api_token = ? WHERE username = ?",
                        (last_logon, token, user_name))
            # dispatch the event
            signal = json.dumps({
                'print': True,
                'message': "{} connected".format(user_name)
            })
            dispatcher.send(signal, sender="Users")
            return token
        finally:
            cur.close()
            self.lock.release()

    def get_user_from_token(self, token):
        conn = self.get_db_connection()

        try:
            self.lock.acquire()
            cur = conn.cursor()
            cur.execute("SELECT id, username, api_token, last_logon_time, enabled, admin FROM users WHERE api_token = ? LIMIT 1", (token,))
            [ id, username, api_token, last_logon_time, enabled, admin ] = cur.fetchone()
            
            return { 'id': id, 'username': username, 'api_token': api_token, 'last_logon_time': last_logon_time, 'enabled': bool(enabled), 'admin': bool(admin) }
        finally:
            cur.close()
            self.lock.release()

    def update_username(self, uid, username):
        """
        Update a user's username.
        Currently only when empire is start up with the username arg.
        """
        conn = self.get_db_connection()
        try:
            self.lock.acquire()
            cur = conn.cursor()

            cur.execute("UPDATE users SET username=? WHERE id=?", (username, uid))

            # dispatch the event
            signal = json.dumps({
                'print': True,
                'message': "Username updated"
            })
            dispatcher.send(signal, sender="Users")
        finally:
            cur.close()
            self.lock.release()

        return True

    def update_password(self, uid, password):
        """
        Update the last logon timestamp for a user
        """
        conn = self.get_db_connection()

        if not self.user_exists(uid):
            return False

        try:
            self.lock.acquire()
            cur = conn.cursor()

            cur.execute("UPDATE users SET password=? WHERE id=?", (self.get_hashed_password(password), uid))

            # dispatch the event
            signal = json.dumps({
                'print': True,
                'message': "Password updated"
            })
            dispatcher.send(signal, sender="Users")
        finally:
            cur.close()
            self.lock.release()

        return True


    def user_logout(self, uid):
        conn = self.get_db_connection()

        try:
            self.lock.acquire()
            cur = conn.cursor()
            cur.execute("UPDATE users SET api_token=null WHERE id=?", (uid,))

            # dispatch the event
            signal = json.dumps({
                'print': True,
                'message': "User disconnected"
            })
            dispatcher.send(signal, sender="Users")

        finally:
            cur.close()
            self.lock.release()

    def refresh_api_token(self):
        """
        Generates a randomized RESTful API token and updates the value
        in the config stored in the backend database.
        """
        # generate a randomized API token
        rng = random.SystemRandom()
        apiToken = ''.join(rng.choice(string.ascii_lowercase + string.digits) for x in range(40))

        return apiToken

    def is_admin(self, uid):
        """
        Returns whether a user is an admin or not.
        """
        conn = self.get_db_connection()
        cur = conn.cursor()
        admin = cur.execute("SELECT admin FROM users WHERE id=?", (uid,)).fetchone()

        if admin[0] == True:
            return True

        return False

    def get_hashed_password(self, plain_text_password):
        if isinstance(plain_text_password,str):
            plain_text_password = plain_text_password.encode('UTF-8')

        return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

    def check_password(self, plain_text_password, hashed_password):
        if isinstance(plain_text_password,str):
            plain_text_password = plain_text_password.encode('UTF-8')
        if isinstance(hashed_password,str):
            hashed_password = hashed_password.encode('UTF-8')

        return bcrypt.checkpw(plain_text_password, hashed_password)

