from django.urls import path
from .views import hotplace, click_address

urlpatterns = [
    path('', hotplace, name='hot-place'),  # hotplace
    path('<str:title>',click_address, name="detail_result")
]
