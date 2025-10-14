import datetime
import json

from post import Post

class Comment:
    def __init__(self, content, author, comment_page, comment_type=0, root_comment=-1):
        self.comment_id = 0
        self.content = content
        self.author = author
        self.root_comment = root_comment
        self.comment_type = comment_type
        self.date_posted = None
        self.comment_page = comment_page
        self.is_published = False
        self.is_root = root_comment == -1
        self.replies = []
    def publish(self, connection, user):
        if not self.is_published:
            self.date_posted = datetime.datetime.now()
            self.is_published = True
            cursor = connection.cursor()
            query = "INSERT INTO comments (content, author, root_comment, date_posted, comment_type, comment_page, replies) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            data = (self.content, self.author, self.root_comment, self.date_posted, self.comment_type, self.comment_page, json.dumps(self.replies))
            cursor.execute(query, data)
            connection.commit()
            self.comment_id = cursor.lastrowid
            cursor.close()
            if self.is_root:
                post = Post.read(connection, self.comment_page)
                post.add_comment(connection, self.comment_id)
            else:
                comment = Comment.read(connection, self.root_comment)
                comment.add_reply(connection, self.comment_id)

        else:
            raise Exception("Post is already published")

    def add_reply(self, connection, comment_id):
        if self.is_root:
            cursor = connection.cursor()
            query = "SELECT replies FROM comments WHERE id=%s"
            cursor.execute(query, (self.comment_id,))
            data = cursor.fetchone()
            if data is None:
                raise NameError("Comment not found")
            else:
                comment_ids = json.loads(data[0])
                comment_ids.append(comment_id)
                query = "UPDATE comments SET replies=%s WHERE id=%s"
                cursor.execute(query, (json.dumps(comment_ids), self.comment_id))
                self.replies.append(Comment.read(connection, comment_id))
                connection.commit()
                cursor.close()
        else:
            raise NameError("Cannot add reply to non-root comment")

    @staticmethod
    def read(connection, comment_id):
        cursor = connection.cursor()
        query = "SELECT * FROM comments WHERE id=%s"
        cursor.execute(query, (comment_id,))
        data = cursor.fetchone()
        if data is None:
            raise NameError("Comment not found")
        else:
            c = Comment(data[1], data[2], data[6], data[5], data[3])
            c.comment_id = data[0]
            c.date_posted = datetime.datetime.strptime(data[4], "%Y-%m-%d %H:%M:%S.%f")
            comment_ids = json.loads(data[7])
            for reply_id in comment_ids:
                c.replies.append(Comment.read(connection, reply_id))
            return c

