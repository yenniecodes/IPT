"""
URL configuration for connectly_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin routes
    path('api-auth/', include('rest_framework.urls')),  # DRF login/logout
    path('posts/', include('posts.urls')),  # Includes all URLs from the posts app

]


# The path('posts/', include('posts.urls')) line connects all the routes in your posts/urls.py file to the posts/ path in your application.
# For example:
# /posts/users/ → Calls get_users.
# /posts/users/create/ → Calls create_user.