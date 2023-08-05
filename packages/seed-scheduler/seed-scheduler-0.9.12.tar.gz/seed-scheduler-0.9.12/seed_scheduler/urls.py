import os
from django.conf.urls import include, url
from django.contrib import admin
from scheduler import views
from rest_framework.authtoken.views import obtain_auth_token

admin.site.site_header = os.environ.get('SCHEDULER_TITLE', 'Scheduler Admin')


urlpatterns = [
    url(r'^admin/',  include(admin.site.urls)),
    url(r'^api/auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/token-auth/', obtain_auth_token),
    url(r'^api/metrics/', views.MetricsView.as_view()),
    url(r'^api/health/', views.HealthcheckView.as_view()),
    url(r'^', include('scheduler.urls')),
    url(r'^docs/', include('rest_framework_docs.urls')),
]
