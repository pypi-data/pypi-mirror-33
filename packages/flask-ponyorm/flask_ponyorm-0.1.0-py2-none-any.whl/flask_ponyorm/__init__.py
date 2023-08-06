from pony.orm import Database

# 
# import authz.models
# import models
# 
# db = FlaskPony(app)
# db.install_models(models, authz.models)
#
# select(u for u in db.User).first()
#


class Pony(Database):
    def __init__(self, app=None):
        super(Pony, self).__init__()
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.bind(**app.config['database'])
        self.generate_mapping()
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['pony'] = self


#db = pony.orm.Database()


#class _EntityMeta(pony.orm.core.EntityMeta):
    #def __new__(cls, name, bases, cls_dict):
        #if hasattr(db, name):
            #return getattr(db, name)
        #return super(_EntityMeta, cls).__new__(cls, name, bases, cls_dict)

    #@pony.orm.core.cut_traceback
    #def __init__(self, name, bases, cls_dict):
        #if hasattr(db, name):
            #self = getattr(db, name)
        #else:
            #super(_EntityMeta, self).__init__(name, bases, cls_dict)


#Entity = db.Entity = type.__new__(_EntityMeta, 'Entity', (pony.orm.core.Entity,), {})
#Entity._database_ = db
