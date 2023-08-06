from .Link import BaseLink, UserLink

class ExportLink(BaseLink):
    display = 'Export'
    url = 'http://google.com'

class ModelLink(BaseLink):
    display = 'Models'
    url = '/dashboard'

class ExportLink(BaseLink):
    display = 'Export'
    url = 'http://google.com'

class ModelLink(BaseLink):
    display = 'Models'
    url = '/dashboard'

class Home(BaseLink):
    display = 'Home'
    url = '/dashboard'

class Logout(UserLink):
    display = 'Logout'
    url = '/logout'

from dashboard.Link import BaseLink, UserLink
from masonite.request import Request

class UserManagementLink(BaseLink):
    display = 'User Management'
    url = '/dashboard/management'
    
    def visible(self, request: Request):
        if request.get_cookie('_real_token'):
            return True
    
    def show(self):
        return self.display

class SwapUserLink(UserLink):
    display = 'Swap Back To User'
    url = '/dashboard/management/swap'

    def visible(self, request: Request):
        if request.get_cookie('_real_token'):
            return True
    
    def show(self):
        return self.display