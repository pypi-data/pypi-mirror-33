''' A User Model Service Provider '''
from masonite.provider import ServiceProvider
import os
from .links import ExportLink, ModelLink, Home, Logout
from .Link import BaseLink, UserLink

package_directory = os.path.dirname(os.path.realpath(__file__))

class DashboardProvider(ServiceProvider):

    wsgi = False 

    def register(self):
       
       # Register static files
        self.app.make('Storage').STATICFILES.update({
            os.path.join(package_directory, 'static'): '_dashboard/' 
        })

        # Register Links
        self.app.bind('HomeLink', Home)

    def boot(self, Storage, ViewClass):
        ViewClass.add_environment('dashboard/templates')
        ViewClass.composer(['/dashboard*', 'dashboard*'], {'nav_links': self.app.collect(BaseLink), 'user_links': self.app.collect(UserLink)})

''' A UserManagementProvider Service Provider '''
from dashboard.links import UserManagementLink, SwapUserLink

class UserManagementProvider(ServiceProvider):

    wsgi = False

    def register(self):
        self.app.bind('UserManagementLink', UserManagementLink)
        self.app.bind('SwapLink', SwapUserLink)

    def boot(self, Request):
        Request.extend(RealUser)

class RealUser:

    def real_user(self):
        if self.get_cookie('_real_token'):
            return User.where('remember_token', self.get_cookie('_real_token')).first()
        
        return None