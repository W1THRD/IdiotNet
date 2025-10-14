import datetime, json
from post import Post
from routes import routes

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.date_created = None
        self.followers = []
        self.following = []
        self.posts = []
        self.liked_posts = []
        self.is_created = False
        self.bio = ""
        self.url = None

    def create(self, connection):
        if not self.is_created:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (self.username,))
            result = cursor.fetchall()
            if len(result) == 0:
                self.is_created = True
                self.date_created = datetime.datetime.now()
                self.url = routes["user"].format(self.username)
                query = "INSERT INTO users (username, date_created, password, followers, posts, following, liked_posts, bio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                data = (self.username, self.date_created, self.password, json.dumps(self.followers), json.dumps(self.posts), json.dumps(self.following),
                        json.dumps(self.liked_posts), self.bio)
                cursor.execute(query, data)
                connection.commit()
                cursor.close()
            else:
                cursor.close()
                raise Exception("User already exists")
        else:
            raise Exception('User already exists')

    def follower_count(self):
        return len(self.followers)

    def add_post(self, connection, post_id:int):
        if self.is_created:
            cursor = connection.cursor()
            cursor.execute("SELECT posts FROM users WHERE username = %s", (self.username,))
            data = json.loads(cursor.fetchone()[0])
            data.append(post_id)
            self.posts = data
            cursor.execute("UPDATE users SET posts = %s WHERE username = %s", (json.dumps(data), self.username))
            connection.commit()
            cursor.close()
        else:
            raise Exception("Cannot add post to nonexistent user")

    def like_post(self, connection, post_id: int, add_like:bool=True):
        if self.is_created:
            cursor = connection.cursor()
            cursor.execute("SELECT liked_posts FROM users WHERE username = %s", (self.username,))
            data = json.loads(cursor.fetchone()[0])
            if (not post_id in data and add_like) or (post_id in data and not add_like):
                if add_like:
                    data.append(post_id)
                else:
                    data.remove(post_id)
                self.posts = data
                cursor.execute("UPDATE users SET liked_posts = %s WHERE username = %s", (json.dumps(data), self.username))
                connection.commit()
                cursor.close()
            else:
                cursor.close()
                raise ValueError("Operation cannot be done")
        else:
            raise NameError("User doesn't exist")

    def add_follower(self, connection, follower, add_follow:bool=True):
        if self.is_created:
            cursor = connection.cursor()
            cursor.execute("SELECT followers FROM users WHERE username = %s", (self.username,))
            follower_data = json.loads(cursor.fetchone()[0])
            cursor.execute("SELECT following FROM users WHERE username = %s", (follower.username,))
            following_data = json.loads(cursor.fetchone()[0])
            can_set_follower = (not follower.username in follower_data and add_follow) or (follower.username in follower_data and not add_follow)
            can_set_following = (not follower.username in follower_data and add_follow) or (follower.username in follower_data and not add_follow)
            if can_set_follower and can_set_following:
                if add_follow:
                    follower_data.append(follower.username)
                    following_data.append(self.username)
                else:
                    follower_data.remove(follower.username)
                    following_data.remove(self.username)
                self.followers = follower_data
                cursor.execute("UPDATE users SET followers = %s WHERE username = %s",
                               (json.dumps(follower_data), self.username))
                cursor.execute("UPDATE users SET following = %s WHERE username = %s",
                               (json.dumps(following_data), follower.username))
                connection.commit()
                cursor.close()
            else:
                cursor.close()
                raise ValueError("Operation cannot be done")
        else:
            raise NameError("User doesn't exist")

    def update_bio(self, connection, bio):
        self.bio = bio
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET bio = %s WHERE username = %s", (bio, self.username))
        connection.commit()
        cursor.close()

    def latest(self, connection, count, offset=0):
        posts = []
        deleted = []
        self.posts.sort(reverse=True)
        for post_id in self.posts[offset:offset+count]:
            try:
                posts.append(Post.read(connection, post_id))
            except NameError:
                deleted.append(post_id)
        self.prune_posts(connection, deleted)
        return posts

    def prune_posts(self, connection, post_ids: list[int]):
        cursor = connection.cursor()
        cursor.execute("SELECT posts FROM users WHERE username = %s", (self.username,))
        self.posts = json.loads(cursor.fetchone()[0])
        for post_id in post_ids:
            self.posts.remove(post_id)
        cursor.execute("UPDATE users SET posts = %s WHERE username = %s", (json.dumps(self.posts), self.username))
        connection.commit()
        cursor.close()

    def liked(self, connection, count, offset=0):
        posts = []
        self.liked_posts.sort(reverse=True)
        for post_id in self.liked_posts[offset:offset+count]:
            posts.append(Post.read(connection, post_id))
        return posts

    @staticmethod
    def read(connection, username:str):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        data = cursor.fetchone()
        if data is None:
            raise NameError("User not found")
        else:
            u = User(username=data[0], password=data[2])
            u.date_created = data[1]
            u.followers = json.loads(data[3])
            u.posts = json.loads(data[4])
            u.following = json.loads(data[5])
            u.liked_posts = json.loads(data[6])
            u.bio = data[7]
            u.is_created = True
            u.url = routes["user"].format(u.username)
            return u