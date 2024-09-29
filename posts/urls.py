from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path("api/list/", views.PostAPIView.as_view(), name="api_post"),
    path('list/', views.PostlistView.as_view(), name='list'),
    path("create/", views.PostcreateView.as_view(), name="create"),
    path('api/create/', views.PostAPIView.as_view(), name='api_create'),

    path('<int:post_id>/update/', views.PostUpdateView.as_view(), name = "update"),

    path("api/<int:post_id>/", views.PostDetailAPIView.as_view()),
    path('<int:post_id>/', views.PostDetailView.as_view(), name='detail'),
    path("<int:post_id>/comments/", views.PostDetailAPIView.as_view()),

    path("api/comments/<int:comment_id>/", views.CommentAPIView.as_view()),
    path("<int:postID>/like/", views.LikeAPIView.as_view()),

    path("api/user/<int:user_id>/", views.UserPostView.as_view()),
    path("api/user/<int:user_id>/like/", views.UserLikedPostView.as_view())
]
