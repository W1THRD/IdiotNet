routes = {
    "home": "/",
    "about": "/about",
    "post": "/posts/{}",
    "latest": "/posts/latest",
    "new_post": "/posts/new",
    "login": "/users/login",
    "signup": "/users/signup",
    "user": "/users/{}",
    "logout": "/users/logout",
    "user_posts": "/users/{}/posts",
    "user_liked_posts": "/users/{}/liked-posts",
    "user_following": "/users/{}/following",
    "user_followers": "/users/{}/followers",
}

API = {
    "like_post": "/api/posts/{}/like",
    "follow_user": "/api/users/{}/follow",
}