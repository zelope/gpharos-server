from django.apps import AppConfig
import sys

class TrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tracker"

    def ready(self):
         # 관리 명령어 실행 시 MQTT 클라이언트를 시작하지 않음
        if 'runserver' in sys.argv:
            from .mqtt_client import start_mqtt_client
            start_mqtt_client()
