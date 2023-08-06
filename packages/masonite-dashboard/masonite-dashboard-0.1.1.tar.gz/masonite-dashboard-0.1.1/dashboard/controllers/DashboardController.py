''' Welcome The User To Masonite '''
from app.User import User
from config.database import DB
from masonite.request import Request

class DashboardController:

    def show(self, request: Request):
        if request.user() and request.user().is_admin:
            return view('/dashboard/templates/dashboard/index')
        
        if request.user():
            request.session.flash('danger', 'You are not an admin')
        return request.redirect('/dashboard/login')
    
    # def single(self):
    #     model = request().app().make('DashboardModels')[request().param('model')]
    #     if model.__table__:
    #         table_name = model.__table__
    #     else:
    #         table_name = model.__name__ + 's'

    #     conn = DB.get_schema_manager().list_table_columns(table_name.lower())
        
    #     model = model.find(request().param('id'))
    #     return view('/dashboard/templates/single', {'model': model, 'getattr': getattr, 'model_schema': conn.items()})

    # def show_all(self):
    #     model = request().app().make('DashboardModels')[request().param('model')]
    #     models = model.all()
    #     return view('/dashboard/templates/show', {'modelclass': model, 'models': models})

    # def update(self):
    #     model = request().app().make('DashboardModels')[request().param('model')]()

    #     model = model.find(request().param('id'))
        
    #     for key in request().all():
    #         if hasattr(model, key):
    #             setattr(model, key, request().input(key))

    #     model.save()
    #     return request().redirect('/dashboard/{}/{}'.format(model.__class__.__name__.lower(), request().param('id'))) \
    #         .session.flash('message', 'Updated Successfully')