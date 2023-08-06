    
from masonite.routes import Get, Post
def routes(prefix='/dashboard'):
    return [
        Get().route('/dashboard', '/dashboard.controllers.DashboardController@show'),
        Get().route('/dashboard/login', '/dashboard.controllers.AuthenticationController@show'),
        Get().route('/dashboard/logout', '/dashboard.controllers.AuthenticationController@logout'),
        Post().route('/dashboard/login', '/dashboard.controllers.AuthenticationController@authenticate'),
        # Get().route('{}/@model:string/@id:int'.format(prefix), '/dashboard.controllers.DashboardController@single'),
        # Get().route('{}/@model:string/@id:int'.format(prefix), '/dashboard.controllers.DashboardController@single'),
        # Get().route('{}/@model:string'.format(prefix), '/dashboard.controllers.DashboardController@show_all'),
        # Post().route('{}/@model:string/@id:int'.format(prefix), '/dashboard.controllers.DashboardController@update')
    ]