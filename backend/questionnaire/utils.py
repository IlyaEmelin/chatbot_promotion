from io import BytesIO
from openpyxl import Workbook
from pathlib import Path
from requests import get
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile
from uuid import uuid4

from django.http import FileResponse

from questionnaire.models import Survey


def get_excel_file(queryset):
    group_by_uuid = {}
    for servey in queryset:
        servey_result = {
            "ФИО пользователя": f"{servey.user.first_name} "
            f"{servey.user.last_name} "
            f"{servey.user.patronymic}"
        }
        # переводим результаты из списка в словарь
        servey_result.update(
            {
                servey.result[i]: servey.result[i + 1]
                for i in range(0, len(servey.result) - 1, 2)
            }
        )
        group_by_uuid.setdefault(servey.questions_version_uuid, []).append(
            servey_result
        )

    with TemporaryDirectory() as report_dir:
        path_dir = Path(report_dir)

        servey_report = Workbook()
        for uuid, results in group_by_uuid.items():
            sheet = servey_report.create_sheet("Mysheet", 0)
            sheet.title = f"{uuid}"
            row = 1
            # заполняем заголовки из первого опроса
            for question in results[0].keys():
                sheet.cell(row=row, column=1, value=question)
                row += 1
            column = 2
            # для каждого опроса
            for result in results:
                row = 1
                # заполняем результаты
                for answer in result.values():
                    sheet.cell(row=row, column=column, value=answer)
                    row += 1
                column += 1

        file_name = str(uuid4()) + ".xlsx"
        file_path = path_dir / file_name
        servey_report.save(file_path)

        # Закрываем workbook чтобы освободить файл
        servey_report.close()

        # Читаем файл в память и создаем ответ
        with open(file_path, "rb") as f:
            file_content = f.read()

        response = FileResponse(
            BytesIO(file_content),
            content_type=(
                "application/"
                "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'

        return response


def get_docs_zip(request, uuid):
    survey = Survey.objects.get(id=uuid)
    documents = survey.docs.all()

    with TemporaryDirectory() as docs_dir:
        path_dir = Path(docs_dir)
        file_name = str(uuid) + ".zip"

        with ZipFile(
            path_dir / file_name,
            "a",
            compression=ZIP_DEFLATED,
            compresslevel=3,
        ) as zip_file:
            for document in documents:
                response = get(document.image)
                if response.status_code == 200:
                    extension = (
                        (
                            document.image.split('filename=')[-1]
                        ).split('&')[0]
                    ).split('.')[-1]
                    image_name = str(uuid4()) + '.' + extension
                    image_path = path_dir / image_name
                    with open(image_path, "wb") as image_file:
                        image_file.write(response.content)
                    zip_file.write(image_path, image_name)

        # Читаем zip-файл в память
        with open(path_dir / file_name, "rb") as f:
            zip_content = f.read()

        response = FileResponse(
            BytesIO(zip_content), content_type="application/zip"
        )
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'

        return response
