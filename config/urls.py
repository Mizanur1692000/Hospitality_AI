from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.agent_core.urls")),
    path("chat/", include("apps.chat_assistant.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("", include("apps.dashboard.urls")),
]
