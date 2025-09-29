import json
import os
import logging
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from questionnaire.models import (
    Question,
    AnswerChoice,
)

logger = logging.getLogger(__name__)

_DEFAULT_PATH = os.sep.join(("static_db_data", "questions"))
_DEFAULT_FILE_NAME = "steps.json"


class Command(BaseCommand):
    help = "Загружает вопросы и варианты ответов из JSON файла"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="step1.json",
            help=(
                "Путь к JSON файлу с данными (по умолчанию: survey_data.json)"
            ),
        )

    def handle(self, *args, **options):
        path, file_name = (
            options.get("path", _DEFAULT_PATH),
            options.get("file_name", _DEFAULT_FILE_NAME),
        )
        logger.debug("Проверяем абсолютный путь или относительный")
        file_path = Path(settings.BASE_DIR) / path / file_name
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)

        try:
            with transaction.atomic():
                self.load_data_from_json(file_path)
                logger.info("Данные успешно загружены из JSON файла!")
        except FileNotFoundError:
            logger.error(f"Файл {file_path} не найден!")
        except json.JSONDecodeError:
            logger.error(f"Ошибка парсинга JSON файла {file_path}")
        except Exception as e:
            logger.error(f"Произошла ошибка: {str(e)}")

    def load_data_from_json(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        questions_data = data.get("questions", [])

        logger.debug("Сначала создаем все вопросы")
        questions = []
        for i, question_data in enumerate(questions_data):
            question = Question.objects.create(
                text=question_data["text"],
                type=question_data["type"],
                external_table_field_name=question_data.get(
                    "external_table_field_name"
                ),
            )
            questions.append(question)
            logger.info(f"Создан вопрос: {question.text}")

        logger.debug(
            "Затем создаем варианты ответов с ссылками на следующие вопросы"
        )
        for i, question_data in enumerate(questions_data):
            current_question = questions[i]

            for answer_data in question_data.get("answers", []):
                next_question_index = answer_data.get("next_question_index")
                next_question = (
                    questions[next_question_index]
                    if next_question_index is not None
                    and next_question_index < len(questions)
                    else None
                )

                AnswerChoice.objects.create(
                    current_question=current_question,
                    next_question=next_question,
                    answer=answer_data["text"],
                )
                logger.info(
                    f'  Создан ответ: {answer_data["text"]} '
                    f'-> {next_question.text if next_question else "КОНЕЦ"}'
                )

        logger.info(f"Итого создано: {len(questions)} вопросов")
        logger.info(
            f"Итого создано: {AnswerChoice.objects.count()} вариантов ответов"
        )
