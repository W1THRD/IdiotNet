import datetime
import json

from routes import routes

class Post:
    def __init__(self, title, content, author):
        self.post_id = 0
        self.title = title
        self.content = content
        self.author = author
        self.date_posted = None
        self.is_published = False
        self.likes = 0
        self.url = None
        self.comments = []

    def publish(self, connection, user):
        if not self.is_published:
            self.date_posted = datetime.datetime.now()
            self.is_published = True
            cursor = connection.cursor()
            query = "INSERT INTO posts (title, content, author, date_posted, likes, comments) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (self.title, self.content, self.author, self.date_posted, self.likes, json.dumps(self.comments))
            cursor.execute(query, data)
            connection.commit()
            self.post_id = cursor.lastrowid
            user.add_post(connection, self.post_id)
            cursor.close()
            self.url = routes["post"].format(self.post_id)
        else:
            raise Exception("Post is already published")

    def like(self, connection, user, add_like:bool=True):
        user.like_post(connection, self.post_id, add_like)
        cursor = connection.cursor()
        cursor.execute("SELECT likes from posts WHERE id=%s", (self.post_id,))
        self.likes = int(cursor.fetchone()[0])
        self.likes += 1 if add_like else -1
        cursor.execute("UPDATE posts SET likes=%s WHERE id=%s", (self.likes, self.post_id,))
        connection.commit()
        cursor.close()

    def add_comment(self, connection, comment_id):
        cursor = connection.cursor()
        cursor.execute("SELECT comments from posts WHERE id=%s", (self.post_id,))
        self.comments = json.loads(cursor.fetchone()[0])
        self.comments.append(comment_id)
        cursor.execute("UPDATE posts SET comments = %s WHERE id=%s", (json.dumps(self.comments), self.post_id))
        connection.commit()
        cursor.close()


    @staticmethod
    def read(connection, post_id:int):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        data = cursor.fetchone()
        if data is None:
            raise NameError("Post not found")
        else:
            p = Post.record_to_object(data)
            return p

    @staticmethod
    def record_to_object(record):
        p = Post(title=record[1], content=record[2], author=record[3])
        p.post_id = record[0]
        p.date_posted = record[4]
        p.likes = record[5]
        p.is_published = True
        p.url = routes["post"].format(p.post_id)
        p.comments = json.loads(record[6])
        return p

    @staticmethod
    def latest(connection, count:int, offset:int=0, sort_by:str="latest"):
        cursor = connection.cursor()
        if sort_by == "latest":
            query = "SELECT * FROM posts ORDER BY date_posted DESC OFFSET %s LIMIT %s"
        elif sort_by == "popular":
            query = "SELECT * FROM posts ORDER BY likes DESC OFFSET %s LIMIT %s"
        else:
            query = "SELECT * FROM posts ORDER BY date_posted DESC OFFSET %s LIMIT %s"
        cursor.execute(query, (offset, count))
        data = cursor.fetchall()
        posts = []
        for record in data:
            p = Post.record_to_object(record)
            posts.append(p)
        return posts
