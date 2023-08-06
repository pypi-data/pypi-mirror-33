from html import escape

from django.db import models

from bots.models import TelegramBot


class VKFeed(models.Model):
    code = models.CharField(max_length=64)
    chat_id = models.CharField(max_length=64)
    owner_id = models.CharField(max_length=64)
    last_id = models.IntegerField(default=-1)
    send_links = models.BooleanField(default=True)
    bot = models.ForeignKey(TelegramBot, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.code




