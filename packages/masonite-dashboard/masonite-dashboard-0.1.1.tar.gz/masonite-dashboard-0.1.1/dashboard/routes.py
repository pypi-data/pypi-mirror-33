    
from masonite.helpers.routes import get, post
from dashboard.controllers.UserManagementController import UserManagementController
def routes(prefix='/dashboard'):
    return [
        get('/dashboard', '/dashboard.controllers.DashboardController@show'),
        get('/dashboard/login', '/dashboard.controllers.AuthenticationController@show'),
        get('/dashboard/logout', '/dashboard.controllers.AuthenticationController@logout'),
        post('/dashboard/login', '/dashboard.controllers.AuthenticationController@authenticate'),
    ]

def management_routes():
    return [
        get('/dashboard/management', UserManagementController.show),
        post('/dashboard/management/login_as_user', UserManagementController.login_as_user),
        get('/dashboard/management/swap', UserManagementController.swap_back_to_user),
        post('/dashboard/management/delete', UserManagementController.delete_user),
        get('/dashboard/management/show', UserManagementController.show_user),
        post('/dashboard/management/create', UserManagementController.create),
    ]
