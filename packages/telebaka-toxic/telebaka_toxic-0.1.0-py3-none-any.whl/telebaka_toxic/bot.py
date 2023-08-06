from django.utils.timezone import now

from telegram import Bot, Update, MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, Filters, CommandHandler, BaseFilter, RegexHandler

from telebaka_toxic.models import ToxicityRating, String


def send_stats(bot: Bot, chat_id, date):
    ratings = ToxicityRating.objects.filter(chat_id=chat_id, date=date).order_by('-rating')
    result = []
    for r in ratings:
        result.append(f' · {r.link}: {r.rating}')
    result = '\n'.join(result)
    bot.send_message(chat_id, f'Список токсичных существ на сегодня:\n\n{result}', parse_mode='html')


def get_string(rating):
    result = String.objects.filter(max_rating__lte=rating).order_by('?').first()
    if result:
        return result.text
    else:
        if rating == -1:
            return 'Кто токсичный? Ну вот кто?'
        else:
            return 'Бип-буп. Осторожно, {link} токсичен. Уровень токсичности: {rating}.'


def stats(bot: Bot, update: Update):
    send_stats(bot, update.effective_message.chat_id, now().date())


def toxic(bot: Bot, update: Update):
    if update.effective_message.reply_to_message:
        r = update.effective_message.reply_to_message
        rating, created = ToxicityRating.objects.update_or_create(
            user_id=r.from_user.id, chat_id=r.chat_id, date=now().date(),
            defaults={
                'username': r.from_user.id,
                'name': r.from_user.full_name
            }
        )
        rating.rating += 1
        rating.save()
        update.effective_message.reply_text(get_string(rating.rating).format(link=rating.link, rating=rating.rating),
                                            parse_mode='html', quote=True)
    else:
        update.effective_message.reply_text(get_string(-1), parse_mode='html', quote=True)


def setup(dispatcher):
    dispatcher.add_handler(CommandHandler('stats', stats))
    dispatcher.add_handler(CommandHandler('toxic', toxic))
    dispatcher.add_handler(RegexHandler(r'[^\w](токс|toxic).*', toxic))
    return dispatcher
