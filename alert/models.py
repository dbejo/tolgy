from django.db import models
from django.utils import timezone

class AlertQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=now))

class Alert(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    objects = AlertQuerySet.as_manager()

    def is_active(self):
        if self.valid_until is None:
            return True
        return self.valid_until >= timezone.now()