# Blog
Backend server for blog application. 
Based on :

 - FastAPI framework + Uvicorn
 - JWT Auth tokens
 - Redis Storage for data storage
 - Redis Storage for cache (2nd instance optimized for caching)
 - Redis OM


## Run
```shell
docker compose up --build
```

## Usage

1. Access the app on <SERVER-IP>:8000
2. Access /docs for Swagger UI with all API endpoints docs


## API endpoints 

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

**NOTE** pk's (primary keys) are generated automatically by Redis OM when creating entities