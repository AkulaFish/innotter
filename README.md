# Innotter
Twitter analogue with its own tips  
Social network API, where you can create you page, tell the world your story!

Models:
- User (Roles: Admin, Moderator, User)
- Page 
- Post
- Tag

Get started with creating account on: 
```
api/register/
```
Then create page on: 
```
api/pages/
```
Make your first post:
```
api/posts/
```
And watch your friends' updates:
```
api/newsfeed/
```

To build and run the application:
```docker
docker-compose up --build 
```
To run tests:
```shell
pytest
```
