from django.db import models
from models import *
from django.utils import timezone
class ModelTracker(models.Model):
    def __init__(self,*args,**kwargs):
        models.Model.__init__(self, *args, **kwargs)
        self.old_state = self.__dict__.copy()

    def save(self, username, force_insert=False, force_update=False, using=None, update_fields=None):
        types=[type("a"),type(1),type({}),type([]),type(("1",2)),type(True),type(1L),type(u"a"),type(1.1),type(None)]
        history = History()
        history.table = self._meta.db_table
        history.done_on = timezone.now()
        history.done_by = username

        history.new_state = self.__dict__.copy()
        history.new_state.pop("old_state")

        if self.pk == None:
            history.old_state = {}
        else:
            history.old_state=self.old_state
        keys2del=[]
        for key in history.old_state:
            if type(history.old_state[key]) not in types:
                if hasattr(history.old_state[key],"toJSON"):
                    history.old_state[key]=history.old_state[key].toJSON()
                elif hasattr(history.old_state[key],"pk"):
                    history.old_state[key]= history.old_state[key].pk
                else:
                    keys2del.append(key)
        for key in keys2del:
            del history.old_state[key]
        keys2del=[]
        for key in history.new_state:
            if type(history.new_state[key]) not in types:
                if hasattr(history.new_state[key], "toJSON"):
                    history.new_state[key] = history.new_state[key].toJSON()
                elif hasattr(history.new_state[key], "pk"):
                    history.new_state[key] = history.new_state[key].pk
                else:
                    keys2del.append(key)
        for key in keys2del:
            del history.new_state[key]

        models.Model.save(self,force_insert=force_insert,force_update=force_update,using=using,update_fields=update_fields)
        history.primary_key=self.pk
        history.new_state.pop("_state","")
        history.old_state.pop("_state","")
        history.save()
    class Meta:
        abstract =True
