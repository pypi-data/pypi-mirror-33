from django.conf import settings
from telegram import Bot, Update, MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, User
from telegram.ext import MessageHandler, Filters, CommandHandler, BaseFilter, CallbackQueryHandler
from dynamic_preferences.registries import global_preferences_registry

from telebaka_lprmerch_poll.models import PollUser, Product, CustomVariant


global_preferences = global_preferences_registry.manager()


def get_user(user: User):
    user, created = PollUser.objects.update_or_create(chat_id=user.id, defaults={
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })
    return user


def start(bot: Bot, update: Update):
    get_user(update.effective_user)
    markup = InlineKeyboardMarkup([])
    text = 'Привет! Это магазин мерча питерского отделения ЛПР. Мы открылись и хотим узнать у вас: что бы вы хотели ' \
           'видеть в нашем магазине.\nСейчас у нас есть вот такие позиции:\n\n'
    for p in Product.objects.all():
        markup.inline_keyboard.append([InlineKeyboardButton(p.title, callback_data=f'product {p.pk}')])
        text += f'・ {p.title}\n'
    markup.inline_keyboard.append([InlineKeyboardButton('[предложить свой вариант]', callback_data='custom')])
    text += 'Что бы вы хотели видеть у нас? Выберите вариант чтобы узнать о нем подробнее.'
    update.effective_message.reply_text(text, reply_markup=markup)
    if update.callback_query:
        update.callback_query.answer()


def product(bot: Bot, update: Update, groups):
    p = Product.objects.get(pk=groups[0])
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('Проголосовать', callback_data=f'vote {p.pk}')],
        [InlineKeyboardButton('< К списку', callback_data='list')],
    ])
    print(f'http://{settings.WEBHOOK_DOMAIN}/{p.image.url}')
    update.callback_query.message.reply_photo(f'https://{settings.WEBHOOK_DOMAIN}/{p.image.url}',
                                              p.description, reply_markup=markup)
    update.callback_query.answer()


def vote(bot: Bot, update: Update, groups):
    p = Product.objects.get(pk=groups[0])  # type: Product
    user = get_user(update.effective_user)
    p.votes.add(user)
    update.callback_query.answer('Спасибо, ваше мнение нам очень важно', show_alert=True)
    start(bot, update)


def custom(bot: Bot, update: Update):
    user = get_user(update.effective_user)
    user.accepting_custom = True
    user.save()
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('[отмена]', callback_data='custom_cancel')]])
    update.effective_message.reply_text('Мы хотим расширять ассортимент: напишите нам, '
                                        'что бы вы ещё хотели видеть в нашем магазине', reply_markup=markup)
    update.callback_query.answer()


def custom_cancel(bot: Bot, update: Update):
    user = get_user(update.effective_user)
    user.accepting_custom = False
    user.save()
    start(bot, update)


def custom_text(bot: Bot, update: Update):
    user = get_user(update.effective_user)
    if user.accepting_custom:
        user.accepting_custom = False
        user.save()
        CustomVariant.objects.create(user=user, text=update.effective_message.text)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton('< К списку', callback_data='list')]])
        update.effective_message.reply_text('Спасибо за ваше участие', reply_markup=markup)
    else:
        start(bot, update)


def setup(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(product, pattern=r'^product (\d+)$', pass_groups=True))
    dispatcher.add_handler(CallbackQueryHandler(vote, pattern=r'^vote (\d+)$', pass_groups=True))
    dispatcher.add_handler(CallbackQueryHandler(custom, pattern=r'^custom$'))
    dispatcher.add_handler(CallbackQueryHandler(custom_cancel, pattern=r'^custom_cancel$'))
    dispatcher.add_handler(CallbackQueryHandler(start, pattern=r'^list$'))
    dispatcher.add_handler(MessageHandler(Filters.text, custom_text))
    return dispatcher
