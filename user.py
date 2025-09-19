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
            cursor.execute("SELECT * FROM users WHERE username = ?", (self.username,))
            result = cursor.fetchall()
            if len(result) == 0:
                self.is_created = True
                self.date_created = datetime.datetime.now()
                self.url = routes["user"].format(self.username)
                query = "INSERT INTO users (username, date_created, password, followers, posts, following, liked_posts, bio) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
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
            cursor.execute("SELECT posts FROM users WHERE username = ?", (self.username,))
            data = json.loads(cursor.fetchone()[0])
            data.append(post_id)
            self.posts = data
            cursor.execute("UPDATE users SET posts = ? WHERE username = ?", (json.dumps(data), self.username))
            connection.commit()
            cursor.close()
        else:
            raise Exception("Cannot add post to nonexistent user")

    def like_post(self, connection, post_id: int, add_like:bool=True):
        if self.is_created:
            cursor = connection.cursor()
            cursor.execute("SELECT liked_posts FROM users WHERE username = ?", (self.username,))
            data = json.loads(cursor.fetchone()[0])
            if (not post_id in data and add_like) or (post_id in data and not add_like):
                if add_like:
                    data.append(post_id)
                else:
                    data.remove(post_id)
                self.posts = data
                cursor.execute("UPDATE users SET liked_posts = ? WHERE username = ?", (json.dumps(data), self.username))
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
            cursor.execute("SELECT followers FROM users WHERE username = ?", (self.username,))
            follower_data = json.loads(cursor.fetchone()[0])
            cursor.execute("SELECT following FROM users WHERE username = ?", (follower.username,))
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
                cursor.execute("UPDATE users SET followers = ? WHERE username = ?",
                               (json.dumps(follower_data), self.username))
                cursor.execute("UPDATE users SET following = ? WHERE username = ?",
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
        cursor.execute("UPDATE users SET bio = ? WHERE username = ?", (bio, self.username))
        connection.commit()
        cursor.close()

    def latest(self, connection, count, offset=0):
        posts = []
        self.posts.sort(reverse=True)
        for post_id in self.posts[offset:offset+count]:
            posts.append(Post.read(connection, post_id))
        return posts

    def liked(self, connection, count, offset=0):
        posts = []
        self.liked_posts.sort(reverse=True)
        for post_id in self.liked_posts[offset:offset+count]:
            posts.append(Post.read(connection, post_id))
        return posts

    @staticmethod
    def read(connection, username:str):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        data = cursor.fetchone()
        if data is None:
            raise NameError("User not found")
        else:
            u = User(username=data[0], password=data[2])
            u.date_created = datetime.datetime.strptime(data[1], "%Y-%m-%d %H:%M:%S.%f")
            u.followers = json.loads(data[3])
            u.posts = json.loads(data[4])
            u.following = json.loads(data[5])
            u.liked_posts = json.loads(data[6])
            u.bio = data[7]
            u.is_created = True
            u.url = routes["user"].format(u.username)
            return u