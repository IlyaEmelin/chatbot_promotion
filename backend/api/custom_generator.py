from drf_yasg.generators import OpenAPISchemaGenerator


class DividedСategoriesSchemaGenerator(OpenAPISchemaGenerator):
    """Кастомный генератор схемы документации."""

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)

        schema.tags = [
            {"name": "For admins", "description": "Административные операции"},
            {"name": "For users", "description": "Операции с пользователями"},
            {"name": "Tokens", "description": "Токены"},
            {"name": "Surveys", "description": "Опросы и анкеты"},
            {"name": "Docs", "description": "Документы опросов"},
            {"name": "Comments", "description": "Комментарии к опросам"},
        ]

        return schema

    def get_operation(self, view, path, prefix, method, components, request):
        operation = super().get_operation(
            view, path, prefix, method, components, request
        )

        if not operation:
            return operation

        path_lower = path.lower()
        method_lower = method.lower()

        if (any(
                i in path_lower
                for i in ["/me", "password", "activation", "username"]
        )
                or path_lower.endswith("/users/") and method_lower == "post"):
            operation.tags = ["For users"]

        elif "users" in path_lower:
            operation.tags = ["For admins"]

        elif "token" in path_lower:
            operation.tags = ["Tokens"]

        elif ("surveys" in path_lower
              and "docs" not in path_lower and "comments" not in path_lower):
            operation.tags = ["Surveys"]

        elif "docs" in path_lower:
            operation.tags = ["Docs"]

        elif "comments" in path_lower:
            operation.tags = ["Comments"]

        else:
            operation.tags = ["Other"]

        return operation