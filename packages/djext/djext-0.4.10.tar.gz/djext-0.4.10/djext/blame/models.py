from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models

UserModel = get_user_model()

on_delete = getattr(settings, 'DJEXT_BLAME_ON_DELETE', models.SET_NULL)
if hasattr(settings, 'DJEXT_BLAME_NULLABLE'):
    null = bool(getattr(settings, 'DJEXT_BLAME_NULLABLE'))
else:
    null = on_delete == models.SET_NULL


class BaseBlameModel(models.Model):
    created_by = models.ForeignKey(UserModel, related_name='+', on_delete=on_delete, null=null)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(UserModel, related_name='+', on_delete=on_delete, null=null)
    updated_on = models.DateTimeField(auto_now=True)

    def get_created_by(self):
        return str(self.created_by or '')

    def get_created_on(self):
        if self.created_on:
            return self.created_on.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return ''

    def get_updated_by(self):
        return str(self.updated_by or '')

    def get_updated_on(self):
        if self.updated_on:
            return self.updated_on.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return ''

    @property
    def created(self):
        if self.pk:
            return f'{self.get_created_by()} on {self.get_created_on()}'
        else:
            return str(None)

    @property
    def updated(self):
        if self.pk:
            return f'{self.get_updated_by()} on {self.get_updated_on()}'
        else:
            return str(None)

    class Meta:
        abstract = True
