from django.shortcuts import render
from django.http import JsonResponse
from .models import User, Post, Comment
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

def get_users(request):
    try:
        users = list(User.objects.values('id', 'username','email','created_at', 'password'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_user(request):
    try:
        data = json.loads(request.body)
        hashed_password = make_password(data['password'])
        user = User.objects.create(username=data['username'], email=data['email'], password=hashed_password)
        user.save() 
        user.refresh_from_db()
        return JsonResponse({'id': user.id, 'message': 'User created successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_posts(request):
    try:
        posts = list(Post.objects.values('id','content', 'created_at'))
        return JsonResponse(posts, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_post(request):
    try:
        data = json.loads(request.body)
        author = User.objects.get(id=data['author_id'])
        post = Post.objects.create(content=data['content'], author=author)
        return JsonResponse({'id': post.id, 'message': 'Post created successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@csrf_exempt
def delete_user(request):
    try:
        if request.method == "DELETE":
            data = json.loads(request.body.decode("utf-8"))
            user_id = data.get("user_id")
            if not user_id:
                return JsonResponse({"error": "User ID is required"}, status=400)
            if data.get("confirm") != "yes":
                return JsonResponse({"error": "Deletion not confirmed"}, status=400)

            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'message': f'User with ID {user_id} deleted successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            return JsonResponse({'message': 'Authentication successful!'}, status=200)
        else:
            return JsonResponse({'message': 'Invalid credentials.'}, status=401)
    return JsonResponse({'message': 'Only POST method is allowed.'}, status=405)

class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListCreate(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

