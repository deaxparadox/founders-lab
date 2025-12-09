from typing import Any

from django.db import models
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.models import User, AbstractBaseUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

    
class BubbleUserModelAbstract(AbstractBaseUser):
    bubble_user_id = models.CharField(_("bubble_user_id"), unique=True)
    bubble_user_email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "bubble_user_email"
    USERNAME_FIELD = "bubble_user_email"
    REQUIRED_FIELDS = ["bubble_user_id"]

    class Meta:
        verbose_name = _("bubble_user")
        verbose_name_plural = _("bubble_user")
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
        
        
class BubbleUserModel(BubbleUserModelAbstract):
    pass

    async def latest_chat_id(self) -> Any:
        if await self.bubble_user_chat_ids.aexists():
            return await self.bubble_user_chat_ids.order_by("-created_at").afirst()
        return None
    