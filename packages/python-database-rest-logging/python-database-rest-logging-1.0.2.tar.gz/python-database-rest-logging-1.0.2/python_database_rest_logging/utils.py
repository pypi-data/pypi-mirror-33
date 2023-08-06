#!/usr/bin/env python
from __future__ import absolute_import, print_function
from flask_security import datastore
from .model import *

class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)
        
    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance

class SessionCopy(UserMixin):

    def __init__(self, **entries):
        self.__dict__.update(entries)

        if "roles" in entries:
            roles = [SessionCopy(**role) for role in entries["roles"]]
            self.roles = roles

    def get_id(self):
        return self.id;

class PonyDatastore(datastore.Datastore):
    def __init__(self):
        super(PonyDatastore,self).__init__(None)

    def commit(self):
        pass

    def copy_model_properties(self,model,current_val):
        model_dict = model.__dict__
        current_val_dict = current_val.to_dict()
        params = {}
        for key in model_dict.keys():
            if key in current_val_dict:
                params[key] = model_dict[key]

        current_val.set(**params)

    @db_session(serializable=True)
    def put(self, model):
        if(model.model_type == "USER"):
            current_val = self.user_model[model.id]
        else:
            current_val = self.role_model[model.id]

        self.copy_model_properties(model,current_val)

    @db_session(serializable=True)
    def delete(self, model):
        if(model.model_type == "USER"):
            current_val = self.user_model[model.id]
        else:
            current_val = self.role_model[model.id]
        current_val.delete()

class PonyUserDatastore(datastore.UserDatastore,PonyDatastore):

    def __init__(self, user_model, role_model):
        self.user_model = user_model
        self.role_model = role_model

    def _is_numeric(self, value):
        try:
            int(value)
        except (TypeError, ValueError):
            return False
        return True

    @db_session(serializable=True)
    def activate_user(user):
        user.active = True


    @db_session(serializable=True)
    def add_role_to_user(self,user,role):
        user.roles.push(role)

    @db_session(serializable=True)
    def create_role(self,**kwargs):
        role = self.role_model(**kwargs)

    @db_session(serializable=True)
    def create_user(self,**kwargs):
        user = self.user_model(**kwargs)

    @db_session(serializable=True)
    def deactivate_user(self,user):
        user.active = False

    @db_session(serializable=True)
    def delete_user(self,user):
        user.delete()

    @db_session(serializable=True)
    def find_or_create_role(self,name, **kwargs):
        try:
            role = self.role_model.get(name = name)
        except ObjectNotFound:
            role = self.role_model(**kwargs)

        if(role != None):
            role_dict = role.to_dict()
            role_dict["model_type"] = "ROLE"
            return SessionCopy(**role_dict)
        else:
            return None

    @db_session(serializable=True)
    def find_role(self,*args, **kwargs):
        role = self.role_model.get(**kwargs)

        if(role != None):
            role_dict = role.to_dict()
            role_dict["model_type"] = "ROLE"
            return SessionCopy(**role_dict)
        else:
            return None

    @db_session(serializable=True)
    def find_user(self,*args, **kwargs):
        user = self.user_model.get(**kwargs)
        if(user != None):
            user_dict = user.to_dict()
            user_dict["model_type"] = "USER"
            user_dict["roles"] = [c.to_dict() for c in user.roles]
            # user_dict["get_auth_token"] = user.get_auth_token()
            return SessionCopy(**user_dict)
        else:
            return None

    @db_session(serializable=True)
    def get_user(self,id_or_email):
        if self._is_numeric(id_or_email):
            user = self.user_model[id_or_email]
        else:
            user = self.user_model.get(email=id_or_email)

        if(user != None):
            user_dict = user.to_dict()
            user_dict["model_type"] = "USER"
            user_dict["roles"] = [c.to_dict() for c in user.roles]
            # user_dict["get_auth_token"] = user.get_auth_token()
            return SessionCopy(**user_dict)
        else:
            return None


    @db_session(serializable=True)
    def remove_role_from_user(self, user, role):
        user.roles.remove(role)

    @db_session(serializable=True)
    def toggle_active(self,user):
        user.active = not user.active


