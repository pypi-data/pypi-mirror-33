''' A User Model Service Provider '''
from masonite.provider import ServiceProvider
import os
from config.dashboard import MODELS
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

        # Register Models
        self.app.bind('DashboardModels', MODELS)

        # Register Links
        self.app.bind('HomeLink', Home)

    def boot(self, Storage, ViewClass):
        ViewClass.add_environment('dashboard/templates')
        ViewClass.composer(['/dashboard*', 'dashboard*'], {'nav_links': self.app.collect(BaseLink), 'user_links': self.app.collect(UserLink)})

class Export:

    def register(app):
        # app.bind('AnotherProviderNavLinks', [
        #     ExportLink()
        # ])
        pass