from html import escape

from django.db import models


class ToxicityRating(models.Model):
    user_id = models.CharField(max_length=64)
    username = models.CharField(max_length=64)
    name = models.TextField()
    chat_id = models.CharField(max_length=64)
    date = models.DateField()
    rating = models.PositiveIntegerField(default=0)

    @property
    def link(self):
        return f'<a href="tg://user?id={self.user_id}">{escape(self.name)}</a>'


class String(models.Model):
    max_rating = models.IntegerField()
    text = models.TextField(help_text='Placeholders: `{warned_link}`, `{warned_rating}`, `{warner_link}`, '
                                      '`{warner_rating}`')

