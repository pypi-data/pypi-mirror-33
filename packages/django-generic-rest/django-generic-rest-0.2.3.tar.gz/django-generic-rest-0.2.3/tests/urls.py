from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from . import views

app_name = 'tests'

router = routers.SimpleRouter()
router.register(r'objects', views.ObjectViewSet, base_name='objects')
urlpatterns = router.urls

urlpatterns = format_suffix_patterns(
    urlpatterns, suffix_required=True, allowed=['json'])
