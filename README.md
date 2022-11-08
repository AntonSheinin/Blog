# Blog
backend server for blog application. 
Based on :
```shell
 - FastAPI framework + Uvicorn
 - JWT Auth tokens
 - Redis Storage for data storage
 - Redis Storage for cache (2nd instance optimized for caching)
 - Redis OM
```

## Run

to run in docker compose

```shell
docker compose up --build
```

## Usage
<<<<<<< HEAD
```shell
1. Access the app on SERVER-IP:8000
2. Access /docs for Swagger UI with all API endpoints docs
```
=======
1. Access the app on server-ip-addr:8000
2. Access /docs for Swagger UI with all API endpoints
>>>>>>> 272490a985a5da2c5479affb9578956a616b2c60

## API endpoints 
```shell
/signup             - Create user (fields to fill: first_name, last_name, email, password)
/login              - User login (fields to fill: email, password)
/me                 - Logged user
/users/{user_pk}    - Update user (fields to fill: user_pk, first_name, last_name)
/users/{user_pk}    - Delete user (fields to fill: user_pk)
/create-blog        - Create blog (filds to fill: title)
/blogs/{blog_pk}    - Get blog (fields to fill: blog_pk)
/blogs/{blog_pk}    - Update blog (fields to fill: blog_pk, title)
/blogs/{blog_pk}    - Delete blog (fields to fill: blog_pk)
/                   - Blog list
/create-post        - Create post (fields to fill: content, blog_pk)
/posts/{post_pk}    - Update post (fields to fill: content)
/posts/{post_pk}    - Delete post (fields to fill: post_pk)
/create-like        - Create like (fields to fill: post_pk)
/likes/{like_pk}    - Delete like (fields to fill: post_pk)
```