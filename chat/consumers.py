from django.contrib.auth import get_user_model
from .models import Chat
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import redis

# Redis 연결 설정
redis_instance = redis.StrictRedis(host='redis', port=6379, db=0)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # 그룹에 참가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 그룹에서 떠남
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # WebSocket에서 메시지를 받으면 실행
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope["user"]  # 현재 연결된 사용자 정보 가져오기

        # Redis에 메시지 저장
        await self.save_message_to_redis(user.username, message)

        # 그룹에 메시지 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # WebSocket으로 메시지 전송
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # Redis에 메시지 저장
    async def save_message_to_redis(self, username, message):
        # Redis에서 room_group_name으로 메시지 리스트 가져오기
        redis_key = f'chat_{self.room_group_name}_messages'
        redis_instance.rpush(redis_key, json.dumps({'user': username, 'message': message}))

        # 메시지가 50개가 넘으면 DB로 저장
        message_count = redis_instance.llen(redis_key)
        if message_count >= 50:
            await self.save_messages_to_db(redis_key)

    # Redis에 있는 메시지들을 DB에 저장
    @database_sync_to_async
    def save_messages_to_db(self, redis_key):
        messages = redis_instance.lrange(redis_key, 0, -1)
        for message in messages:
            message_data = json.loads(message)
            User = get_user_model()
            user = User.objects.get(username=message_data['user'])  # 유저 객체 찾기   
            Chat.objects.create(user=user, message=message_data['message'])

        # Redis 메시지 삭제
        redis_instance.delete(redis_key)

