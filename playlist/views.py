import requests, base64, urllib.parse
from django.core.cache import cache
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PlaylistSerializer
from WhateverSong.config import CLIENT_ID, CLIENT_SECRET, TOKEN_URL
from django.shortcuts import get_object_or_404
from .models import Playlist
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from accounts.models import User
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TOKEN_URL = os.getenv('TOKEN_URL')

# 토큰 발급
def get_access_token():
    # 'spotify_access_token' key값으로 value를 가져온다.
    access_token = cache.get('spotify_access_token')    
    if access_token is None:    # 캐시 안에 토큰이 존재하지 않으면 아래의 로직 진행
        encoded = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8"))
        headers = {
            'Authorization': f'Basic {encoded.decode("utf-8")}',
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
        }
        response = requests.post(TOKEN_URL, headers=headers, data=data)

        if response.status_code != 200:
            return None

        response_data = response.json()
        access_token = response_data.get('access_token')
        expires_in = 30*60      # 30분을 초 단위로 변환

        # 토큰을 캐시에 저장하고 30분 후에 만료
        cache.set('spotify_access_token', access_token, timeout=expires_in)
    return access_token 
    # return JsonResponse({'access_token': access_token})


# playlist 조회
class PlaylistDataAPIView(APIView):
    def get(self, request):
        # 캐시 확인
        cache_key = 'playlist_data'
        cache_data = cache.get(cache_key)

        if cache_data:
            # 캐시 데이터가 있을 때 인증된 사용자일 경우 DB에 저장
            if request.user.is_authenticated:
                for item in cache_data:
                    Playlist.objects.get_or_create(
                        playlist_id=item['id'],
                        defaults={
                            "name": item['name'],
                            "link": item['link'],
                            "image_url": item['image_url'],
                            "user": request.user    # 인증된 사용자만 저장
                        }
                    )
            return Response(cache_data, status=200)

        access_token = get_access_token()
        if not access_token:
            return Response({"error": "토큰이 유효하지 않습니다."}, status=400)

        # spotify api 호출 헤더
        headers = {"Authorization": f"Bearer {access_token}"}

        # spotify api 호출
        spotify_api = requests.get(
            "https://api.spotify.com/v1/browse/featured-playlists?limit=40", headers=headers
        )
        spotify_data = spotify_api.json()
        
        playlists = []
        for item in spotify_data.get("playlists", {}).get("items", []):
            playlist_data = {
                "name": item["name"],  # 플레이리스트 이름
                "link": item["external_urls"]["spotify"],  # 플레이리스트 링크
                "image_url": (
                    item["images"][0]["url"] if item["images"] else None
                ),  # 플레이리스트 이미지 URL (있는 경우)
                "id": item["id"],
            }

            # DB에 플레이리스트 데이터 저장
            if request.user.is_authenticated:
                Playlist.objects.get_or_create(
                    user = request.user,
                    playlist_id=playlist_data['id'],
                    defaults={
                        "name": playlist_data['name'],
                        "link": playlist_data['link'],
                        "image_url": playlist_data['image_url'],
                    }
                )
            playlists.append(playlist_data)

        # 캐시에 저장
        cache.set(cache_key, playlists, timeout=1*60)
        # print(f"캐시에 저장된 데이터: {cache_key} -> {playlists}")
        return Response(playlists, status=200)

# playlist 검색
class PlaylistSearchAPIView(APIView):
    def get(self, request):
        search = request.query_params.get("query", None)

        # 캐시에서 데이터 확인 
        cache_key = f'playlist_search_{search}'     # 검색어마다 고유한 캐시 생성
        cache_playlist = cache.get(cache_key)

        if cache_playlist:
            # 캐시 데이터가 있을 때도 DB에 저장
            for item in cache_playlist:
                Playlist.objects.get_or_create(
                    playlist_id=item['id'],
                    defaults={
                        "name": item['name'],
                        "link": item['link'],
                        "image_url": item['image_url'],
                        # "user": request.user if request.user.is_authenticated else None  # 사용자 정보 없이 저장
                    }
                )
            return Response(cache_playlist, status=200)
        
        # 로컬 DB에서 동일한 검색어로 저장된 플레이리스트 확인
        # __icontains : 특정 문자가 포함된 것을 찾을 때 사용 (대소문자를 구분하지 않음)
        playlist_in_db = Playlist.objects.filter(name__icontains=search)
        if playlist_in_db.exists():
            serializer = PlaylistSerializer(playlist_in_db, many=True)
            cache.set(cache_key, serializer.data, timeout=1*60)   
            # print(f"캐시에 저장된 데이터: {cache_key} -> {serializer.data}")
            return Response(serializer.data, status=200)

        # 캐시와 DB에 없으면 Spotify API 호출
        access_token = get_access_token()
        if not access_token:
            return Response({"error": "토큰이 유효하지 않습니다."}, status=400)

        # spotify api 호출 헤더, 검색 api에 전달할 파라미터
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"q": search, "type": "playlist"}

        # spotify api 호출
        spotify_api = requests.get(
            "https://api.spotify.com/v1/search?limit=40", headers=headers, params=params
        )

        spotify_data = spotify_api.json()

        playlists = []
        for item in spotify_data.get("playlists", {}).get("items", []):
            playlist_data = {
                "name": item["name"],  # 플레이리스트 이름
                "link": item["external_urls"]["spotify"],  # 플레이리스트 링크
                "image_url": (
                    item["images"][0]["url"] if item["images"] else None
                ),  # 플레이리스트 이미지 URL (있는 경우)
                "id": item["id"],
            }

            # 로컬 DB에 저장
            Playlist.objects.get_or_create(
                playlist_id=playlist_data['id'],
                defaults={
                    "name": playlist_data['name'],
                    "link": playlist_data['link'],
                    "image_url": playlist_data['image_url']
                }
            )
            playlists.append(playlist_data)

        # 캐시에 저장
        cache.set(cache_key, playlists, timeout=1*60)
        # print(f"캐시에 저장된 데이터: {cache_key} -> {playlists}")
        return Response(playlists, status=200)


# Spotify API 데이터 변경 시 DB, 캐시 업데이트
class PlaylistUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        search = request.query_params.get('query', None)

        # 캐시 확인
        cache_key = f'playlist_search_{search}'
        cache_playlist = cache.get(cache_key)

        if cache_playlist:
            return Response(cache_playlist, status=200)
        
        access_token = get_access_token()
        if not access_token:
                return Response({'error' : '토큰이 유효하지 않습니다.'}, status=400)

        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"q": search, "type": "playlist"}

        spotify_api = requests.get(
            "https://api.spotify.com/v1/search?limit=40", headers=headers, params=params
        )
        spotify_data = spotify_api.json()

        playlists = []
        for item in spotify_data.get("playlists", {}).get("items", []):
            # API에서 가져온 데이터를 DB에서 업데이트
            playlist, created = Playlist.objects.update_or_create(
                playlist_id=item["id"],
                defaults={
                    "name": item["name"],
                    "link": item["external_urls"]["spotify"],
                    "image_url": item["images"][0]["url"] if item["images"] else None
                }
            )

            playlist_data = {
                "name": playlist.name,
                "link": playlist.link,
                "image_url": playlist.image_url,
                "id": playlist.playlist_id,
            }

            playlists.append(playlist_data)

        # 캐시에 저장
        cache.set(cache_key, playlists, timeout=1*60)

        return Response(playlists, status=200)


class PlaylistZzimAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, playlist_id):
        user = request.user
        playlist = Playlist.objects.filter(user=user, playlist_id=playlist_id) # 플레이리스트 유무 확인
        # 플레이리스트가 존재하면 삭제
        if playlist.exists():
            playlist.delete()
            return Response({'message':'찜하기가 취소 되었습니다.'}, status=200)
        # 플레이리스트가 존재하지 않으면 추가
        else:
            new_playlist = Playlist.objects.create(user=user, playlist_id=playlist_id)
            serializer = PlaylistSerializer(new_playlist)
            return Response({'message':'찜하기가 추가 되었습니다.', 'playlist':serializer.data}, status=200)
        
# 유저가 찜한 플레이리스트 확인하는 뷰
class UserZzimPlaylistsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        playlists = Playlist.objects.filter(user=user)
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data, status=200)

class PlaylistPageView(TemplateView):
    template_name = "playlist/playlist.html"

# 특정 유저의 찜한 플레이리스트 조회하는 뷰
class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        access_token = get_access_token()
        if not access_token:
            return Response({"error": "토큰이 유효하지 않습니다."}, status=400)

        # spotify api 호출 헤더
        headers = {"Authorization": f"Bearer {access_token}"}

        # spotify api 호출
        spotify_api = requests.get(
            "https://api.spotify.com/v1/browse/featured-playlists", headers=headers
        )
        spotify_data = spotify_api.json()

        playlists = []
        for item in spotify_data.get("playlists", {}).get("items", []):
            if Playlist.objects.filter(user=user, playlist_id=item["id"]).exists():
                playlist = {
                    "name": item["name"],  # 플레이리스트 이름
                    "link": item["external_urls"]["spotify"],  # 플레이리스트 링크
                    "image_url": (
                        item["images"][0]["url"] if item["images"] else None
                    ),  # 플레이리스트 이미지 URL (있는 경우)
                    "id": item["id"],
                }        
                playlists.append(playlist)
        return Response(playlists, status=200)