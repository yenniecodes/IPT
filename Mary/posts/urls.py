from django.urls import path
from .import views
from .views import UserListCreate, PostListCreate, CommentListCreate
from django.urls import include

urlpatterns = [
    path('users/', views.get_users, name='get_users'),
    path('users/create/', views.create_user, name='create_user'),
    path('posts/', views.get_posts, name='get_posts'), 
    path('posts/create/', views.create_post, name='create_post'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('login/', views.login_view, name='login'),
    path('delete_user/', views.delete_user, name='delete_post'),
    path('edit-username/', views.edit_username, name='edit_username'),
    path('edit-post/', views.EditPostView.as_view(), name='edit_post'),
    path('delete-post/', views.DeletePostView.as_view(), name='delete_post'),
    path('create-comment/', views.CreateCommentView.as_view(), name='create_comment'),
    path('post-details/', views.PostDetailView.as_view(), name='post_detail'),
    path('delete-comment/', views.DeleteCommentView.as_view(), name='delete_comment'),
    path('edit-comment/', views.EditCommentView.as_view(), name='edit_comment'),
    ]