import re
from django.utils.timezone import now

from telegram import Bot, Update, User
from telegram.ext import MessageHandler, Filters, CommandHandler, BaseFilter, RegexHandler

from telebaka_toxic.models import ToxicityRating, String


TOXIC_PHRASES = [
    r'наху[йя]',
    r'[оа]?ху[йёиел]',
    r'пизд',
    r'(за|вы)?[её]б',
    r'токс',
    r'залуп',
    r'дерьм',
    r'мраз[ьио]',
    r'светов',
    r'бур[яа]ков',
    r'(вы)?бл[яэ][дт]',
    r'(обо|на)?сс[аы]',
    r'(обо|на)?ср[аи]',
    r'пер[джн]',
    r'пук',
    r'мусор',
    r'чь?мо',
    r'ло[хш]',
    r'пид[оа]р',
    r'говн',
    r'муд[аи]',
    r'сос[иау]',
    r'[вш]инд',
    r'подави',
    r'мамк?',
]


def send_stats(bot: Bot, chat_id, date):
    ratings = ToxicityRating.objects.filter(chat_id=chat_id, date=date, rating__gt=0).order_by('-rating')
    result = []
    for r in ratings:
        result.append(f' · {r.name}: {r.rating}')
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
            return 'Бип-буп. Осторожно, {warned_link} токсичен. Уровень токсичности: {warned_rating}.'


def stats(bot: Bot, update: Update):
    send_stats(bot, update.effective_message.chat_id, now().date())


def add_toxicity(value, chat_id, user: User):
    rating, created = ToxicityRating.objects.update_or_create(
        user_id=user.id, chat_id=chat_id, date=now().date(),
        defaults={
            'username': user.username,
            'name': user.full_name
        }
    )
    rating.rating += value
    rating.save()
    return rating


def toxic(bot: Bot, update: Update):
    if update.effective_message.reply_to_message:
        r = update.effective_message.reply_to_message

        if update.effective_user.id == r.from_user.id:
            return

        warned_rating = add_toxicity(3, update.effective_message.chat_id, r.from_user)
        warner_rating = add_toxicity(5, update.effective_message.chat_id, r.from_user)
        update.effective_message.reply_text(get_string(warned_rating.rating).format(warned_link=warned_rating.link,
                                                                                    warned_rating=warned_rating.rating,
                                                                                    warner_link=warner_rating.link,
                                                                                    warner_rating=warner_rating.rating),
                                            parse_mode='html', quote=True)
    else:
        update.effective_message.reply_text(get_string(-1), parse_mode='html', quote=True)


def regex(bot: Bot, update: Update):
    m = update.effective_message
    rating, created = ToxicityRating.objects.update_or_create(
        user_id=m.from_user.id, chat_id=m.chat_id, date=now().date(),
        defaults={
            'username': m.from_user.id,
            'name': m.from_user.full_name
        }
    )
    for phrase in TOXIC_PHRASES:
        if re.search(r'^(.*[^\w])?' + phrase, update.effective_message.text, re.IGNORECASE):
            rating.rating += 1
    rating.save()


def setup(dispatcher):
    dispatcher.add_handler(CommandHandler('stats', stats))
    dispatcher.add_handler(CommandHandler('toxic', toxic))
    dispatcher.add_handler(CommandHandler('warn', toxic))
    dispatcher.add_handler(MessageHandler(Filters.text, regex))
    return dispatcher
