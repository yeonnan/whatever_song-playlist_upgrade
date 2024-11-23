import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Chat
from accounts.models import User

redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

class ChatConsumer(AsyncWebsocketConsumer):
    # 연결 요청을 받으면
    async def connect(self):
        # 해당 방을 번호로 지정하기
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        
        # 채널 레이어 그룹에 사용자 추가하기
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        # 추가 했으니 승인 보내주기
        await self.accept()
    
    # 연결이 종료되면
    async def disconnect(self, _):
        #채널 레이어 그룹에 사용자 삭제하기
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    #메세지를 받으면
    async def receive(self, text_data):
        # 유저랑 메세지 받아주고
        data = json.loads(text_data)
        user = data['user']
        message = data['message']

        #유저랑 메세지 캐시에 넣어주고
        await self.message_to_cache(user, message)

        #그룹에 보내주기
        await self.channel_layer.group_send(
            self.room_name,{
                'type' : 'chat_message',
                'user' : user,
                'message' : message,
            }
        )

    #채팅 메세지를 받으면 
    async def chat_message(self, event):
        user = event['user'],
        message = event['message']
        #유저한테 보내주기 
        await self.send(text_data=json.dumps({
            'user' : user,
            'message' : message,
        }))

    async def message_to_cache(self, user, message):
        redis_client.xadd(self.room_name, {'user': user, 'message': message})
        
        # 10개 이상이면 db로 보내줌
        cache_length = redis_client.xlen(self.room_name)
    
        if cache_length >= 10:
            await self.cache_to_db()

            #메세지 db로 보내고캐시 지워주기
            redis_client.delete(self.room_name)

    # 캐시 정보 db에 넣어주는 함수
    async def cache_to_db(self):
        messages = redis_client.xrange(self.room_name)

        for message_id, data in messages:
            user = data['user']
            message = data['message']
            
            await sync_to_async(Chat.objects.create)(
                room_name = self.room_name,
                user = await sync_to_async(User.objects.get)(nickname=user),
                message = message
                )