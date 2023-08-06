''' Welcome The User To Masonite '''
from masonite.view import View
from masonite.facades.Auth import Auth


class AuthenticationController:

    def show(self, view: View):
        """ Show Login Page """
        return view.render('/dashboard/templates/dashboard/login')

    def authenticate(self, Request):
        user = Auth(Request).login(Request.input('username'), Request.input('password'))
        if user and user.is_admin:
           return Request.redirect('/dashboard')
        elif not user:
            Request.session.flash('danger', 'Username or password is incorrect')
        else:
            Request.session.flash('danger', 'User does not have admin priviledges')
        
        Request.redirect('/dashboard/login')   

    def logout(self, Request):
        Auth(Request).logout()
        return Request.redirect('/dashboard/login')