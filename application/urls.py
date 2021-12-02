from django.urls import path, include
from .views import *
from . import views
from django.views.generic import ListView, DetailView
from django.conf.urls import url
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', LoginView.as_view(), name='authorization'),# path('', views.authorization),
    # url('client_list', ListView.as_view(queryset=Client.objects.all(), template_name="client_list")),
    path('worker_list', WorkerListView.as_view(), name='workers/worker_list'),
    path('agent_list', AgentListView.as_view(), name='agents/agent_list'),
    path('worker_card/<int:pk>/', views.worker_card, name='workers/worker_card'),
    path('delete_image/<int:pk>/', views.delete_image, name='delete_image'),
    path('agent_card/<int:pk>/', views.agent_card, name='agents/agent_card'),
    path('add_worker', views.add_worker, name='workers/add_worker'),
    path('add_agent', views.add_agent, name='agents/add_agent'),
    path('account', AccountView.as_view(), name='account'),
    path('client_list', ClientListView.as_view(), name='clients/client_list'),
    path('client_card/<int:pk>/', ClientCardView.as_view(), name='clients/client_card'),
    path('add_client', views.add_client, name='clients/add_client'),
    path('logout', LogoutView.as_view(next_page='authorization'), name='logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)