"""Hook into Alliance Auth"""

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls
from .views import workflows_dashboard

class WorkflowMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Workflows"),
            "fas fa-list-check fa-fw",
            "workflows:index",
            navactive=["workflows:"],
        )

    def render(self, request):
        """Render the menu item"""

        if request.user.has_perm("workflows.basic_access"):
            return MenuItemHook.render(self, request)

        return ""


class WorkflowDashboardHook(hooks.DashboardItemHook):
    def __init__(self):
        super().__init__(workflows_dashboard,1)

@hooks.register("menu_item_hook")
def register_menu():
    """Register the menu item"""

    return WorkflowMenuItem()


@hooks.register("url_hook")
def register_urls():
    """Register app urls"""

    return UrlHook(urls, "workflows", r"^flows/")

@hooks.register('dashboard_hook')
def register_dashboard_hook():
    return WorkflowDashboardHook()
