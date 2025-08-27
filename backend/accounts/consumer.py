import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("admins", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("admins", self.channel_name)

    async def send_notification(self, event):  # 👈 matches "type" in group_send
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "timestamp": event["timestamp"]
        }))

