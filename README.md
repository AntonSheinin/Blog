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
METHOD  URL                     DESCRIPTION

POST    /signup                 Create user (fields to fill in JSON: first_name, last_name, email, password)
POST    /login                  User login (fields to fill in form: email, password)
GET     /me                     Logged user
PUT     /update-me              Update logged user (fields to fill in JSON Request: first_name, last_name)
DELETE  /delete-me              Delete logged user
POST    /create-blog            Create blog (filds to fill in JSON Request: title)
GET     /blogs/{blog_pk}        Get blog (url to fill: blog_pk)
PUT     /blogs/{blog_pk}        Update blog (url to fill: blog_pk, field to fill in JSON Request: title)
DELETE  /blogs/{blog_pk}        Delete blog (url to fill: blog_pk)
GET     /                       Blog list
POST    /create-post/{blog_pk}  Create post (url to fill: blog_pk, fields to fill in JSON Request: content)
PUT     /posts/{post_pk}        Update post (url to fill: post_pk, fields to fill in JSON Request: content)
DELETE  /posts/{post_pk}        Delete post (url to fill: post_pk)
POST    /create-like/{post_pk}  Create like (url to fill: post_pk)
DELETE  /likes/{like_pk}        Delete like (url to fill: like_pk)

**NOTE** pk's (primary keys) are generated automatically by Redis OM when creating entities