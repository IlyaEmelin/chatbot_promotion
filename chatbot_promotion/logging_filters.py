import inspect
import logging


class ClassMethodFilter(logging.Filter):
    """Фильтр для добавления имени класса и метода в лог"""

    def filter(self, record):
        """
        Получаем информацию о вызывающем коде

        Args:
            record: запись лога

        Returns:
            bool: Успешность
        """
        frame = inspect.currentframe()
        try:
            while frame:
                frame = frame.f_back
                if not frame:
                    break

                locals_dict = frame.f_locals

                if "self" in locals_dict:
                    instance = locals_dict["self"]
                    class_name = instance.__class__.__name__

                    method_name = frame.f_code.co_name

                    record.class_name = class_name
                    record.method_name = method_name
                    return True

                elif "cls" in locals_dict:
                    cls = locals_dict["cls"]
                    class_name = cls.__name__
                    method_name = frame.f_code.co_name

                    record.class_name = class_name
                    record.method_name = method_name
                    return True

        except Exception:
            record.class_name = "UnknownClass"
            record.method_name = "unknown_method"
            return True

        record.class_name = "Function"
        record.method_name = (
            frame.f_code.co_name if frame else "unknown_method"
        )
        return True
