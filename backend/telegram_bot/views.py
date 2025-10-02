import logging
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from asgiref.sync import async_to_sync

from .bot import bot

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def webhook(request):
    try:
        logger.debug("Получаем данные из запроса")
        update_data = json.loads(request.body.decode("utf-8"))

        logger.debug("Обрабатываем обновление асинхронно")

        # Используем async_to_sync для правильного управления event loop
        async_to_sync(bot.process_webhook_update)(update_data)

        return JsonResponse({"status": "ok"})

    except json.JSONDecodeError as e:
        logger.error("Ошибка декодирования JSON: %s", str(e))
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON"},
            status=400,
        )
    except Exception as e:
        logger.error(
            "Ошибка webhook телеграмм бота %s",
            str(e),
            exc_info=True,
        )
        return JsonResponse({"status": "error", "message": str(e)})
