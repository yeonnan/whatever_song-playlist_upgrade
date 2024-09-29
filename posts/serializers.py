from rest_framework import serializers
from accounts.models import User
from .models import Post, Comment
from accounts.models import User

class CommentSerializer(serializers.ModelSerializer):
    user_image = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['post']

    def get_user_image(self, obj):
        return obj.user.image.url if obj.user.image else None

class PostSerializer(serializers.ModelSerializer):
    #게시글에서 댓글 보이게 수정
    comments = CommentSerializer(many = True, read_only = True)
    author = serializers.PrimaryKeyRelatedField(queryset = User.objects.all())
    comments_count = serializers.IntegerField(source = 'comments.count', read_only = True)
    like_count = serializers.IntegerField(source = 'like.count', read_only = True)
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author', 'like', 'created_at', 'updated_at']
