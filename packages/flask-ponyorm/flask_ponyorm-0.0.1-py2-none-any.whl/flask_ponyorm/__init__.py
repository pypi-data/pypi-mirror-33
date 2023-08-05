import pony.orm
import pony.orm.core


db = pony.orm.Database()


class _EntityMeta(pony.orm.core.EntityMeta):
    def __new__(cls, name, bases, cls_dict):
        if hasattr(db, name):
            return getattr(db, name)
        return super(_EntityMeta, cls).__new__(cls, name, bases, cls_dict)

    @pony.orm.core.cut_traceback
    def __init__(self, name, bases, cls_dict):
        if hasattr(db, name):
            self = getattr(db, name)
        else:
            super(_EntityMeta, self).__init__(name, bases, cls_dict)


Entity = db.Entity = type.__new__(_EntityMeta, 'Entity', (pony.orm.core.Entity,), {})
Entity._database_ = db
