from django.urls import path

from .views import (
    agent_index,
    agent_status,
    agent_view,
)
from .views_safe import SafeAgentServiceView

urlpatterns = [
    path("", agent_index, name="agent-index"),  # ✅ /api/
    path("status/", agent_status, name="agent-status"),  # ✅ /api/status/
    path("agent/", agent_view, name="agent"),  # ✅ /api/agent/ (unified endpoint for all tasks)
    path("agent/safe/", SafeAgentServiceView.as_view(), name="agent-safe"),  # ✅ /api/agent/safe/ (safe endpoint for business insight cards)
]
