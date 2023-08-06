from django.db import models


class PollUser(models.Model):
    chat_id = models.CharField(max_length=64)
    username = models.CharField(max_length=32, null=True)
    first_name = models.TextField()
    last_name = models.TextField(null=True)
    accepting_custom = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Product(models.Model):
    title = models.CharField(max_length=32)
    image = models.ImageField()
    description = models.TextField(max_length=255)
    votes = models.ManyToManyField(PollUser, blank=True)
    weight = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return self.title

    class Meta(object):
        ordering = ['weight']


class CustomVariant(models.Model):
    text = models.TextField()
    user = models.ForeignKey(PollUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'#{self.id} by {self.user}'
