# Project : Whatever song?
본인의 노래 실력 측정과 플레이리스트를 나눌 수 있는 커뮤니티 사이트

## Project Introduction
- AI를 이용하여 녹음본과 유튜브 원곡 음원의 보컬 추출 후 음정 비교 시스템 제공
- Spotify의 플레이리스트 API를 사용하여 플레이리스트 제공
- user가 직접 플레이리스트를 만들고 올릴 수 있는 게시판

## Development time
2024.05.13 ~ 2024.06.12

## Development Environment
- Programming Language : Python 3.10
- Framework : DJANGO, DRF
- Database : PostgreSQL, Redis
- Deployment : AWS (EC2, S3), Docker, Gunicorn, Nginx, Ubuntu
- FrontEnd : Html, CSS, JS
- Version Control : Git, GitHub
- Communication Tool : Notion, Figma, Slack, Zep

## Requirements
- Li-brosa : 음악 및 오디오 신호 처리를 위한 파이썬 라이브러리, 피치 분석, 주파수 도메인 변환에서 유리한 라이브러리라서 선택
- Spleeter : 노래에서 mr과 보컬을 분리해내는 기술, 음원 분리가 가능한 모델 중에서 속도와 품질이 적합해서 채택
- Matplotlib : 데이터 시각화를 위한 파이썬 라이브러리, 음정을 사용자에게 보여주는 시각화를 위한 그래프 라이브러리 채택

## Deployment
프로젝트 배포 링크

## Installation
1. 깃허브 클론
```
https://github.com/Gold-Children/whatever_song.git
```
2. python 패키지 설치
```
pip install -r requirements.txt
```
3. Django migration 진행
```
python manage.py makemigrations
python manage.py migrate
```
4. Django server 실행
```
python manage.py runserver
```
5. Django 서버를 켠 상태에서 Redis server 실행
```
redis-server
```

## API Documentation
api 명세서

## Apps Description
### 1. Coach
- 유튜브 음원 및 유저 음원 파일 보컬 추출
- 추출 파일 비교 후 결과물 그래프 시각화
- 그래프 분석 후 점수 및 훈수
### 2. Playlist
- 외부 API (spotify) 연동
- 실시간 플레이리스트를 가져와서 추천
- 원하는 키워드로 검색해서 결과 반환
- 찜하기 기능으로 로그인한 유저의 프로필에서 해당 플레이리스트 확인 가능
### 3. Post CRUD
- 게시글 작성, 수정, 삭제
- 게시글 검색 기능
- 좋아요순, 최신순으로 정렬 기능
- 노래 추천 게시판, 자유 게시판 카테고리 기능
### 4. Comment CRUD
- 댓글 작성, 수정, 삭제
- 댓글에 프로필 사진을 누르면 해당 user의 프로필 페이지로 이동
### 5. User 
- 이메일 인증을 이용한 회원가입 기능
- JWT을 이용한 로그인 및 로그아웃
- 회원 가입한 ID, Password, Nickname, Image 수정
- post의 좋아요 및 playlist의 찜하기 기능 저장
- 유저가 게시한 게시글 확인
- 훈수를 받았던 내용 확인

## ERD
![image](https://github.com/Gold-Children/whatever_song/assets/145152442/4b9340ac-10fa-4ca0-b9a2-2fe8d501d641)
