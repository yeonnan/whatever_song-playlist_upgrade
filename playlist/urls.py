from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.PlaylistPageView.as_view(), name="playlist"),
    path("data/", views.PlaylistDataAPIView.as_view(), name="playlist-data"),
    path("search/", views.PlaylistSearchAPIView.as_view(), name="playlist-search"),
    path("zzim/<str:playlist_id>/", views.PlaylistZzimAPIView.as_view(), name="playlist-zzim"),
    path("user-zzim/", views.UserZzimPlaylistsAPIView.as_view(), name="user-zzim"),

    path("profile-zzim/<int:user_id>/", views.UserProfileAPIView.as_view(), name="user-profile-zzim"),

    # token cache postman
    path('get_access_token/', views.get_access_token, name='get_access_token'),
]
