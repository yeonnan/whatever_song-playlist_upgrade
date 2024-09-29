from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.generic import TemplateView
from django.contrib.auth import (
    get_user_model,
    authenticate,
    update_session_auth_hash,
    logout,
)
from django.shortcuts import render
from django.http import JsonResponse
from .serializers import SignupSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.db import transaction
from .serializers import SignupSerializer, CustomTokenObtainPairSerializer
from .models import User

class SignUpView(CreateAPIView):
    model = get_user_model()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]


class SignUpPageView(TemplateView):
    template_name = "accounts/signup.html"

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LoginPageView(TemplateView):
    template_name = "accounts/login.html"

class LogoutAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        except Exception as e:
            print(f"Exception: {e}")  # 예외 메시지 출력
        return Response(status=status.HTTP_205_RESET_CONTENT)


def main(request):
    return render(request, "accounts/main.html")


# Create your views here.
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    # 프로필 보기
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = SignupSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfilePageView(TemplateView):
    template_name = "accounts/profile.html"

class ProfileUpdatePageView(TemplateView):
    template_name = "accounts/profile_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_id"] = kwargs.get("pk")
        context["csrf_token"] = self.request.META.get("CSRF_COOKIE")
        return context


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user != user:
            return Response(
                {"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = SignupSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # 사용자명(ID)
            new_username = serializer.validated_data.get("username")
            if (
                new_username
                and User.objects.exclude(pk=user.pk)
                .filter(username=new_username)
                .exists()
            ):
                return Response(
                    {"error": "이미 존재하는 이름입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 닉네임
            new_nickname = serializer.validated_data.get("nickname")
            if (
                new_nickname
                and User.objects.exclude(pk=user.pk)
                .filter(nickname=new_nickname)
                .exists()
            ):
                return Response(
                    {"error": "이미 존재하는 닉네임입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 이메일 중복 확인
            new_email = serializer.validated_data.get("email")
            if (
                new_email
                and User.objects.exclude(pk=user.pk).filter(email=new_email).exists()
            ):
                return Response(
                    {"error": "이미 사용중인 이메일입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "프로필 수정 및 토큰 재발급이 완료되었습니다.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user != user:
            return Response({"error": "권한 읍서요"}, status=status.HTTP_403_FORBIDDEN)

        # 이미지 수정
        serializer = SignupSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            with transaction.atomic():
                image_file = request.data.get("image")
                if image_file:
                    # 기존 이미지 삭제
                    user.image.delete()
                    user.image.save(image_file.name, image_file, save=True)
                    serializer.validated_data["image"] = user.image

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    # 패스워드 변경
    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user != user:
            return Response({"error": "권한이 없음."}, status=status.HTTP_403_FORBIDDEN)

        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return Response(
                {"error": "현재 비밀번호가 올바르지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if current_password == new_password:
            return Response(
                {"error": "이전 비밀번호와 같은 비밀번호로 설정할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 해싱된 비밀번호를 저장
        user.set_password(new_password)
        user.save()

        # 세션 갱신
        update_session_auth_hash(request, user)

        return Response(
            {"message": "비밀번호가 성공적으로 변경되었습니다."},
            status=status.HTTP_200_OK,
        )


class ProfiledeleteView(APIView):
    permission_classes = [IsAuthenticated]

    # 회원 탈출
    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if request.user != user:
            return Response(
                {"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        logout(request._request)
        user.delete()

        return Response(
            {"message": "회원 탈퇴 성공하셨습니다"}, status=status.HTTP_204_NO_CONTENT
        )