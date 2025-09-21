# from django.db.models import Model, BigIntegerField, CharField, DateTimeField
#
#
# class TelegramUser(Model):
#     """Пользователь телеграмма"""
#
#     chat_id = BigIntegerField(unique=True)
#     username = CharField(max_length=100, blank=True, null=True)
#     first_name = CharField(max_length=100, blank=True, null=True)
#     last_name = CharField(max_length=100, blank=True, null=True)
#     created_at = DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.username or self.first_name} ({self.chat_id})"
