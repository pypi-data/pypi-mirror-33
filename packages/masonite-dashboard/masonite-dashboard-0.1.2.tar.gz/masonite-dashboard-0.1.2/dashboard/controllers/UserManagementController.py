""" User Management """
from masonite.facades.Auth import Auth
from masonite.helpers import password
from masonite.request import Request
from masonite.view import View

from config.auth import AUTH
from config.database import DB


class UserManagementController:
    """ User Management Controller """

    __auth__ = AUTH['model']
    template_prefix = '/dashboard/templates/dashboard'

    def show(self, view: View, request: Request):
        if request.input('search'):
            users = self.__auth__.all().filter(lambda user: self.search(request.input('search'), user))
        else:
            users = self.__auth__.all()

        return view.render('{0}/management/management'.format(self.template_prefix), {'users': users})

    def search(self, search, item):
        if search.lower() in item.name.lower():
            return True

        if search.lower() in item.email.lower():
            return True


    def login_as_user(self, request: Request):
        if not request.get_cookie('_real_token'):
            request.cookie('_real_token', request.get_cookie('token'))

        Auth(request).login_by_id(request.input('user'))
        return request.redirect('/dashboard')


    def swap_back_to_user(self, request: Request):
        if request.get_cookie('_real_token'):
            request.cookie('token', request.get_cookie('_real_token'))
            request.delete_cookie('_real_token')

        return request.redirect('/dashboard')


    def delete_user(self, request: Request):
        self.__auth__.find(request.input('user')).delete()

        return request.redirect('/dashboard/management')


    def show_user(self, view: View):
        conn = DB.get_schema_manager().list_table_columns('users')
        return view.render('{0}/management/add_user'.format(self.template_prefix), {'schema': conn})


    def create(self, request: Request):
        del request.request_variables['csrf_token']

        # if POST /api/users
        proxy = self.__auth__()

        for field, value in request.all().items():
            if value:
                print(field)
                if field == 'password':

                    setattr(proxy, field, password(request.input('password')))
                else:
                    setattr(proxy, field, value)

        proxy.save()

        return request.redirect('/dashboard/management')
