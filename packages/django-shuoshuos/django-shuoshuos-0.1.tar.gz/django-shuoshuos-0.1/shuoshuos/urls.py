from django.urls import path

from . import views
app_name='shuoshuos'
urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:shuoshuo_id>/', views.detail, name='detail'),
    path('<int:shuoshuo_id>/vote/', views.vote, name='vote'),
]
