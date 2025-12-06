# notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Pour l’instant on accepte tout
        await self.accept()

        # Message de bienvenue (debug)
        await self.send(
            text_data=json.dumps(
                {
                    "type": "welcome",
                    "message": "Connexion WebSocket OK 🚀",
                }
            )
        )

    async def receive(self, text_data=None, bytes_data=None):
        # Echo basique pour tester
        if text_data:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "echo",
                        "received": text_data,
                    }
                )
            )

    async def disconnect(self, close_code):
        # Tu pourras nettoyer ici (group_discard...) plus tard
        pass
