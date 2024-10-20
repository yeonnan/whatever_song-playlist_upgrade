# python
FROM python:3.10.14

# 디렉토리
WORKDIR /app

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    python3-dev \
    libhdf5-dev \
    gcc \
    musl-dev \
    ffmpeg \
    && apt-get clean

# requirements.txt 복사
COPY requirements.txt /app/

# pip 업그레이드 및 종속성 설치
RUN pip install --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn  # Add this line to install gunicorn


# 애플리케이션 코드 복사
COPY . .

# 포트
EXPOSE 8000

# 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# CMD ["daphne", "WhateverSong.asgi:application"]