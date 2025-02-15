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
from django.shortcuts import get_object_or_404

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

@csrf_exempt  # Use this only if you are testing without CSRF tokens (for API-based requests)
def edit_username(request):
    if request.method == "POST":
        try:
            # Parse JSON body
            data = json.loads(request.body.decode("utf-8"))
            user_id = data.get("user_id")
            new_username = data.get("username")

            # Fetch user or return error
            user = get_object_or_404(User, id=user_id)

            if new_username and new_username != user.username:
                if User.objects.filter(username=new_username).exists():
                    return JsonResponse({"error": "Username already taken."}, status=400)
                else:
                    user.username = new_username
                    user.save()
                    return JsonResponse({"success": "Username updated successfully!"})
            else:
                return JsonResponse({"error": "Invalid username or same as current one."}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)

    return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

class CreateCommentView(APIView):
    def post(self, request):
        # Extract post_id, author_id, and text from request data
        post_id = request.data.get("post_id")
        author_id = request.data.get("author_id")
        text = request.data.get("text")  # Adjusted field name to match model

        # Validate input fields
        if not post_id or not author_id or not text:
            return Response({"error": "post_id, author_id, and text are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure post and author exist
        post = get_object_or_404(Post, id=post_id)
        author = get_object_or_404(User, id=author_id)

        # Create the comment
        comment = Comment.objects.create(post=post, author=author, text=text)

        # Serialize and return the new comment
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PostDetailView(APIView):
    def get(self, request):
        # Retrieve all posts
        posts = Post.objects.all()
        post_list = []
        
        for post in posts:
            post_author_username = post.author.username if post.author else "Unknown"
            post_serializer = PostSerializer(post)
            post_data = post_serializer.data
            
            post_data = {
                "id": post_data["id"],
                "content": post_data["content"],
                "author": post_data["author"],
                "author_username": post_author_username,
                "created_at": post_data["created_at"]
            }

            # Retrieve and serialize comments related to the post
            comments = Comment.objects.filter(post=post)
            comment_serializer = CommentSerializer(comments, many=True)
            
            post_list.append({
                "post": post_data,
                "comments": comment_serializer.data
            })

        return Response({"posts": post_list}, status=status.HTTP_200_OK)
        
class DeleteCommentView(APIView):
    def delete(self, request):
        # Extract comment_id from request data
        comment_id = request.data.get("comment_id")

        # Validate input field
        if not comment_id:
            return Response({"error": "comment_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the comment
        comment = get_object_or_404(Comment, id=comment_id)

        # Delete the comment
        comment.delete()

        return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class EditCommentView(APIView):
    def put(self, request):
        # Extract comment_id and new text from request data
        comment_id = request.data.get("comment_id")
        new_text = request.data.get("text")

        # Validate input fields
        if not comment_id or not new_text:
            return Response({"error": "comment_id and text are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the comment
        comment = get_object_or_404(Comment, id=comment_id)

        # Update the comment text
        comment.text = new_text
        comment.save()

        # Serialize and return the updated comment
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

        
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

class DeletePostView(APIView):
    def delete(self, request):
        # Extract post_id from the JSON request body
        post_id = request.data.get("post_id")

        # Validate if post_id is provided
        if not post_id:
            return Response({"error": "post_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the post object based on post_id from JSON
        post = get_object_or_404(Post, id=post_id)

        # Delete the post (Anyone can delete)
        post.delete()

        return Response({"success": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class EditPostView(APIView):
    def put(self, request):
        # Extract post_id from the JSON request body
        post_id = request.data.get("post_id")

        # Validate if post_id is provided
        if not post_id:
            return Response({"error": "post_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the post object based on post_id from JSON
        post = get_object_or_404(Post, id=post_id)

        # Validate only the existing fields are updated (e.g., content)
        serializer = PostSerializer(post, data=request.data, partial=True)  # Allows partial updates

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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

@csrf_exempt  # Remove this if using CSRF tokens
def create_comment(request):
    if request.method == "POST":
        try:
            # Parse JSON body
            data = json.loads(request.body.decode("utf-8"))
            post_id = data.get("post_id")
            author_id = data.get("author_id")
            content = data.get("content")

            # Fetch post and author
            post = get_object_or_404(Post, id=post_id)
            author = get_object_or_404(User, id=author_id)

            # Validate content
            if not content or content.strip() == "":
                return JsonResponse({"error": "Comment content cannot be empty."}, status=400)

            # Create the comment
            comment = Comment.objects.create(post=post, author=author, content=content)

            return JsonResponse({
                "success": "Comment added successfully!",
                "comment_id": comment.id,
                "post_title": post.title,
                "author": author.username,
                "content": comment.content
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User (author) not found."}, status=404)

    return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

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

