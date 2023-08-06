from html import escape

from django.db import models

from bots.models import TelegramBot


class User(models.Model):
    user_id = models.CharField(max_length=64)
    bot = models.ForeignKey(TelegramBot, on_delete=models.CASCADE,
                            limit_choices_to={'plugin_name': 'telebaka_anonymous_chat'})

    def __str__(self):
        return self.user_id

