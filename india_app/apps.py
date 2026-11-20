from django.apps import AppConfig


class IndiaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'india_app'


import threading

class IndiaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'india_app'  # Aapke app ka naam

    def ready(self):
        # Server start hote hi background me MongoDB ko "wake up" karega
        def warmup_mongo():
            try:
                from .attendance_views import collection_A, collection_B
                if collection_A is not None:
                    collection_A.find_one()
                if collection_B is not None:
                    collection_B.find_one()
                print("⚡ MongoDB Cluster Woken Up Successfully!")
            except Exception as e:
                print("Warmup error:", e)

        # Thread me chalayenge taaki Django startup slow na ho
        threading.Thread(target=warmup_mongo, daemon=True).start()
