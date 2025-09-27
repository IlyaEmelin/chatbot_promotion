import logging
import asyncio

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .bot import bot

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def webhook(request):
    try:
        logger.debug("Получаем данные из запроса")
        update_data = json.loads(request.body.decode("utf-8"))

        logger.debug("Обрабатываем обновление асинхронно")

        asyncio.run(bot.process_update(update_data))

        return JsonResponse({"status": "ok"})
    except Exception as e:
        logger.error(
            "Запуска webhook телеграмм бота %s",
            str(e),
            exc_info=True,
        )
        return JsonResponse({"status": "error", "message": str(e)})
