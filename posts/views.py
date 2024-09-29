from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Post, Comment
from accounts.models import User
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .serializers import PostSerializer, CommentSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Count, Q
from urllib.parse import unquote
import uuid

class PostAPIView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        search_query = unquote(request.GET.get('search', ''))
        category = request.GET.get('category')
        sort = request.GET.get('sort', '-created_at')
        page_number = request.GET.get('page', 1)
        page_size = 20

        posts = Post.objects.all()

        if search_query:
            posts = posts.filter(
                Q(title__icontains=search_query) | Q(content__icontains=search_query) | Q(author_nickname__icontains=search_query)
            )

        if category:
            posts = posts.filter(category=category)

        posts = posts.annotate(likes_count=Count('like'))

        if sort == "-like":
            posts = posts.order_by('-likes_count', '-created_at')
        else:
            posts = posts.order_by(sort)

        paginator = Paginator(posts, page_size)
        paginated_posts = paginator.get_page(page_number)

        serializer = PostSerializer(paginated_posts, many=True)
        return Response({
            'posts': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': paginated_posts.number
        }, status=status.HTTP_200_OK)

    def post(self, request):
        request.data.image = f'accounts_{uuid.uuid4()}.png'
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class PostlistView(TemplateView):
    template_name = "posts/list.html"

class PostcreateView(TemplateView):
    template_name = "posts/create.html"


class PostDetailAPIView(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, post_id):
        return get_object_or_404(Post, pk=post_id)
    
    def get(self, request, post_id):
        post = self.get_object(post_id)
        serializer = PostSerializer(post)
        data = serializer.data

        like = False
        if request.user.is_authenticated:
            if request.user.id in data['like']:
                like = True
        data = {'data':data, 'like':like}
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, post_id):
        post = self.get_object(post_id)
        serializer = PostSerializer(
            post, data=request.data, partial=True) 
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    def delete(self, request, post_id):
        post = self.get_object(post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #댓글 작성
    def post(self, request, post_id):
        post = self.get_object(post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(TemplateView):
    template_name = "posts/detail.html"

class PostUpdateView(TemplateView):
    template_name = "posts/update.html"


class CommentAPIView(APIView):

    def get_object(self, comment_id):
        return get_object_or_404(Comment, pk=comment_id)

    def put(self, request, comment_id):
        comment = self.get_object(comment_id)
        serializer = CommentSerializer(
            comment, data=request.data, partial=True) 
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    def delete(self, request, comment_id):
        comment = self.get_object(comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class LikeAPIView(APIView):
    def get_object(self, postID):
        return get_object_or_404(Post, pk=postID)
    
    def post(self, request, postID):
        post = self.get_object(postID)
        if post.like.filter(pk=request.user.id).exists():
            post.like.remove(request.user.id)
        else:
            post.like.add(request.user.id)
        return Response(status=status.HTTP_200_OK)
    
class UserPostView(APIView):

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        posts = Post.objects.filter(author=user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLikedPostView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        liked_posts = user.post_likes.all()
        serializer = PostSerializer(liked_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)