from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("chat/", views.chat_view, name="chat"),
    path("kpi-analysis/", views.kpi_analysis_view, name="kpi_analysis"),
    path("hr-solutions/", views.hr_solutions_view, name="hr_solutions"),
    path("beverage/", views.beverage_view, name="beverage"),
    path("menu-engineering/", views.menu_engineering_view, name="menu_engineering"),
    path("recipes/", views.recipes_view, name="recipes"),
    path("cost-analysis/", views.cost_analysis_view, name="cost_analysis"),
    path("strategic-planning/", views.strategic_planning_view, name="strategic_planning"),
    path("kpi-dashboard/", views.kpi_dashboard_view, name="kpi_dashboard"),
    path("modern-kpi/", views.modern_kpi_dashboard_view, name="modern_kpi_dashboard"),
]
