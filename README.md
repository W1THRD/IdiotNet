# IdiotNet
IdiotNet is a really stupid social media, made by [W1THRD](https://w1thrd.x10.mx/). 
It has very little security features, and at this stage is only a prototype, not a finished
product intended for the public internet.

## Record-Objects
Each database table has a corresponding class to represent a record from said table.
There are two constructors for each:
- default constructor: `User()`, `Comment()`, `Post()`, and `Token()` create a new object that hasn't been committed to the database yet
- read constructor: `.read()` will take a pre-existing record from the database and turn it into an object

If you need to commit an object to the database, use `Comment.publish`, `User.create`, `Post.publish`, or `Token.create`

## Database
Please, I beg you, don't yell at me for storing the passwords in plaintext.
I've known for years that this is not a good way to store passwords.
I will add it sometime in the future.
Here's a rundown of the tables used:

### Posts
This table stores all the user-generated content. Each record contains:
- `id`: A unique numeric id
- `title`: user-created title for the posts
- `content`: user-created body for the post
- `author`: username of the user who created the post
- `date_posted`: the date of the post's creation, in Unix time
- `likes`: a count of how many users have liked the posts

When the backend reads a record from the posts database, it will create an instance
of the `Post` class, containing the same data values.

### Comments
This table stores comments on posts and (eventually) user profiles. Each record includes:
- `id`: unique numeric ID
- `content`: text in the comment
- `author`: username of the comment's author
- `root-comment`: the main comment in the thread, defaults to -1 if the comment isn't a reply
- `date_posted`: the date of the comment's creation, in Unix time
- `comment-type`: 0 for post comments, 1 for user comments
- `comment-page`: the post id or username of the comment's location
- `replies`: a JSON list of the ID's of replies to the comment

### Users
This table stores data about user accounts, including:
- `username`: a string used to identify a user, by both the backend and in the UX
- `date_created`: the date of the user's registration, in Unix time
- `password`: the password, stored in plaintext. (Don't be mad- I will start using password hashing and salting in a future update)
- `followers`: a JSON list of the usernames of the user's followers
- `posts`: a JSON list of the ID's of posts the user has written
- `following`: a JSON list of the users that this user follows
- `liked_posts`: a  JSON list of the ID's of posts the user has liked

Like with records in the posts database, all records in the User database can be stored in `User` object.

### Tokens
This table stores authentication tokens, used to keep track of who is logged in. The data stored includes:
- `id`: a unique UUID string to identify a token
- `username`: the username of the user associated with the token
- `valid_until`: expiration date of the token, will eventually be implemented
