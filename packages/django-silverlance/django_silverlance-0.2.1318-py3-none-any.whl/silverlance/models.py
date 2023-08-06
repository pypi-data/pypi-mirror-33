from django.conf import settings
from django.db import models
from socket import gethostname
from uuid import uuid4


_hostname = gethostname()

def _default_hostname():
    return _hostname


class AbstractReplicatableModel(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+', on_delete=models.CASCADE, editable=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+', on_delete=models.CASCADE, editable=False)
    created_on = models.CharField(max_length=255, default=_default_hostname)
    modified_on = models.CharField(max_length=255, default=_default_hostname)

    class Meta:
        abstract = True
