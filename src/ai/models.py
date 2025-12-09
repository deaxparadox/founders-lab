import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from bubbleio.models import BubbleUserModel


class AgentChatIDModel(models.Model):
    bubble_user = models.ForeignKey(
        BubbleUserModel, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="bubble_user_chat_ids",
        verbose_name=_("Bubble user")
    )
    chat_id = models.CharField(
        verbose_name=_("Agent chat id"),
        unique=True
    )
    chat_name = models.CharField(
        default="New Chat",
        max_length=60,
        verbose_name=_("Chat name"),
    )
    deleted = models.BooleanField(verbose_name=_("Chat ID deleted"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class TokenUsage(models.Model):
    bubble_user = models.ForeignKey(
        BubbleUserModel, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="bubble_user_token_usage",
        verbose_name=_("Bubble user")
    )
    token_count = models.IntegerField(default=60000, verbose_name=_("Token count"))
    token_used = models.IntegerField(default=0, verbose_name=_("Token used"))
    
    async def token_available(self):
        return self.token_used <= self.token_count