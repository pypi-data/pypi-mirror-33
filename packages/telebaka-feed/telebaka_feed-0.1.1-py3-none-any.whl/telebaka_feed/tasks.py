from celery import shared_task
from dynamic_preferences.registries import global_preferences_registry
from telegram import Bot, TelegramError
from vk_advanced_api import VKAPI
from raven.contrib.django.raven_compat.models import client

from bots.message_types import PhotoMessage
from telebaka_feed.models import VKFeed


global_preferences = global_preferences_registry.manager()


def get_vk_photo(attachment):
    for size in (2560, 1280, 807, 604, 130, 75):
        if f'photo_{size}' in attachment:
            return attachment[f'photo_{size}']
    return None


@shared_task
def stats():
    vk_api = VKAPI(access_token=global_preferences['feed__vk_api_token'])
    for vk_feed in VKFeed.objects.all():
        try:
            bot = Bot(vk_feed.bot.token)
            wall_data = vk_api.utils.wall.get(owner_id=vk_feed.owner_id)
            for post in reversed(wall_data['items']):
                if post['id'] > vk_feed.last_id:
                    try:
                        if post['text']:
                            bot.send_message(vk_feed.chat_id, post['text'])
                        if 'attachments' in post:
                            photos = []
                            for image in filter(lambda a: a['type'] == 'photo', post['attachments']):
                                photos.append(get_vk_photo(image))
                            PhotoMessage(photos, vk_feed.chat_id).send(bot)
                        if vk_feed.send_links:
                            bot.send_message(vk_feed.chat_id, f"https://vk.com/wall{post['owner_id']}_{post['id']}",
                                             disable_web_page_preview=True)
                    except Exception:
                        client.captureException()
                    vk_feed.last_id = post['id']
            vk_feed.save()
        except Exception:
            client.captureException()
