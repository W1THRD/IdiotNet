from datetime import datetime, timedelta
import uuid

from user import User

class Token:
    def __init__(self, user_id):
        self.token_id = str(uuid.uuid4())
        self.user_id = user_id
        self.valid_until = None
        self.is_created = False
    def create(self, connection):
        if not self.is_created:
            try:
                user = User.read(connection, self.user_id)
            except Exception as e:
                raise Exception("User not found")
            self.valid_until = datetime.now() + timedelta(days=7)
            self.is_created = True
            cursor = connection.cursor()
            query = "INSERT INTO tokens (id, user_id, valid_until) VALUES (%s, %s, %s)"
            data = (self.token_id, self.user_id, self.valid_until)
            cursor.execute(query, data)
            connection.commit()
            cursor.close()
        else:
            raise Exception("Token already exists")

    @staticmethod
    def read(connection, token_id):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tokens WHERE id = %s", (token_id,))
        data = cursor.fetchone()
        if data is None:
            print(f"{token_id} not found")
            raise NameError("Token not found")
        else:
            t = Token(data[1])
            t.token_id = token_id
            t.valid_until = data[2]
            t.is_created = True
            return t
