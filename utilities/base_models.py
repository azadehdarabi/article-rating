from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    uuid = models.UUIDField(verbose_name=_("UUID"), editable=False, default=uuid4)
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)
    updated_time = models.DateTimeField(verbose_name=_("Updated time"), auto_now=True)
    created_time = models.DateTimeField(verbose_name=_("Created time"), auto_now_add=True)

    class Meta:
        abstract = True
