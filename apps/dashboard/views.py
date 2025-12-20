from django.shortcuts import render
from django.http import Http404
from django.template import TemplateDoesNotExist


def _render_dashboard_page(request, template_name, page_title=None, extra_context=None):
    """
    Helper function to render dashboard pages with common context.
    
    Args:
        request: Django request object
        template_name: Name of the template file (without 'dashboard/' prefix)
        page_title: Optional page title for context
        extra_context: Optional dict of additional context variables
    
    Returns:
        Rendered template response
    
    Raises:
        Http404: If template does not exist
    """
    context = {
        'page_title': page_title or template_name.replace('_', ' ').title(),
        'template_name': template_name,
    }
    
    # Merge any extra context provided
    if extra_context:
        context.update(extra_context)
    
    try:
        return render(request, f"dashboard/{template_name}.html", context)
    except TemplateDoesNotExist:
        raise Http404(f"Template 'dashboard/{template_name}.html' not found")


def dashboard_view(request):
    """
    Main dashboard view for the hospitality AI agent
    """
    context = {
        'dashboard_stats': {
            'total_pages': 10,
            'features': ['KPI Analysis', 'HR Solutions', 'Beverage Management', 
                        'Menu Engineering', 'Recipes', 'Strategic Planning'],
        }
    }
    return _render_dashboard_page(request, "index", "Main Dashboard", context)


def chat_view(request):
    """
    Dedicated chat page for focused conversations
    """
    return _render_dashboard_page(request, "chat", "Chat Assistant")


def kpi_analysis_view(request):
    """
    KPI Analysis page with core tasks and chat functionality
    """
    return _render_dashboard_page(request, "kpi_analysis", "KPI Analysis")


def hr_solutions_view(request):
    """
    HR Solutions page with core tasks and chat functionality
    """
    return _render_dashboard_page(request, "hr_solutions", "HR Solutions")


def beverage_view(request):
    """
    Beverage Management page with core tasks and chat functionality
    """
    return _render_dashboard_page(request, "beverage", "Beverage Management")


def menu_engineering_view(request):
    """
    Menu Engineering page with core tasks and chat functionality
    """
    return _render_dashboard_page(request, "menu_engineering", "Menu Engineering")


def recipes_view(request):
    """
    Recipe Management page with core tasks and chat functionality
    """
    return _render_dashboard_page(request, "recipes", "Recipe Management")


def strategic_planning_view(request):
    """
    Strategic Planning page with core tasks and chat functionality
    """
    return _render_dashboard_page(request, "strategic_planning", "Strategic Planning")


def kpi_dashboard_view(request):
    """
    KPI Dashboard page with comprehensive monitoring and chat functionality
    """
    return _render_dashboard_page(request, "kpi_dashboard", "KPI Dashboard")


def modern_kpi_dashboard_view(request):
    """
    Modern, colorful KPI Dashboard with engaging design
    Mobile-responsive with interactive charts
    """
    return _render_dashboard_page(request, "modern_kpi_dashboard", "Modern KPI Dashboard")
