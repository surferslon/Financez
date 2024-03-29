from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


class Currency(models.Model):
    name = models.CharField(max_length=255)
    selected = models.BooleanField(blank=True, default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.selected:
            Currency.objects.filter(user=self.user).exclude(pk=self.pk).update(selected=False)
