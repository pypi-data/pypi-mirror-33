from celery import shared_task
from django.utils.timezone import now
from telegram import Bot

from telebaka_toxic.bot import send_stats
from telebaka_toxic.models import ToxicityRating


@shared_task
def stats(bot_token):
    bot = Bot(bot_token)
    date = now().date()
    chats_ids = set(ToxicityRating.objects.filter(date=date).values_list('chat_id', flat=True))
    for chat_id in chats_ids:
        send_stats(bot, chat_id, date)
