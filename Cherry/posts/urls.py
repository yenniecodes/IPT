from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_users, name='get_users'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),  # This is crucial
    path('posts/', views.get_posts, name='get_posts'),
    path('posts/create/', views.create_post, name='create_post'),
    path('users/update/<int:user_id>/', views.update_user, name='update_user'),
]


# What This Does
# The urlpatterns list maps specific URLs to the corresponding view functions in posts/views.py.
# users/ → Calls get_users to retrieve all users.
# users/create/ → Calls create_user to create a new user.
# posts/ → Calls get_posts to retrieve all posts.
# posts/create/ → Calls create_post to create a new post.