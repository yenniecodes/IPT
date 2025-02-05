from django.db import models
from django.contrib.auth.models import AbstractUser

class User(models.Model): 
    username = models.CharField(max_length=100, unique=True)  
    email = models.EmailField(unique=True)  
    password = models.CharField(max_length=128)  # Add a password field
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self): 
        return self.username
    
class Post(models.Model): 
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return self.content[:50] 


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"