from django.db import models

class TelegramMessage(models.Model):
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['timestamp']

class BotMessage(TelegramMessage):
    user_message = models.OneToOneField("telegram.UserMessage", on_delete=models.CASCADE, related_name='bot_message')

    def __str__(self):
        return f"BotMessage for Bot {self.user_message_id} at {self.timestamp}"
    
    class Meta:
        abstract = False

class UserMessage(TelegramMessage):
    user_id = models.IntegerField(db_index=True)
    chat_id = models.IntegerField(db_index=True)
    bot_message: BotMessage | None

    def __str__(self):
        return f"UserMessage for User {self.user_id} at {self.timestamp}"
    
    class Meta:
        abstract = False

class Alert(models.Model):
    text = models.TextField()
    def __str__(self):
        return f"Alert for Users: {self.text}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from telegram.tasks import send_alert
        send_alert.delay(self.id)

    class Meta:
        abstract = False

class TelegramSummary(models.Model):
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    def __str__(self):
        return f"TelegramSummary for Users: {self.text}"
    
    class Meta:
        abstract = False
        ordering = ['timestamp']

