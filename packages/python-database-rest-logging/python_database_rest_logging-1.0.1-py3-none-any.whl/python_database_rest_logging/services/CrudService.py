from pony.orm import *
from pony.orm import count as orm_count

class CrudService:

    def __init__(self, db_object):
        self.db_object = db_object

    @db_session(serializable=True)
    def get_all_dict_datatables(self,start,length,draw,search,order,columns):
        query = self.db_object.select()
        count = select(orm_count(c) for c in self.db_object)
        count_filtered = select(orm_count(c) for c in self.db_object)

        if search is not None and search["value"] != "":
            try:
                search_query = lambda o: getattr(self.db_object,"label").startswith(search["value"]) or getattr(self.db_object,"label").endswith(search["value"])
                query = query.filter(search_query)
                count_filtered = select(orm_count(o) for o in self.db_object if getattr(o,"label").startswith(search["value"]) or getattr(o,"label").endswith(search["value"]))
            except:
                pass

            try:
                search_query = lambda o: getattr(o,"name").startswith(search["value"]) or getattr(o,"name").endswith(search["value"])
                query = query.filter(search_query)
                count_filtered = select(orm_count(o) for o in self.db_object if getattr(o,"name").startswith(search["value"]) or getattr(o,"name").endswith(search["value"]))
            except:
                pass

        if order is not None:
            column_index = order[0]["column"]

            if order[0]["dir"] == "desc":
                query = query.order_by(desc(getattr(self.db_object,columns[column_index]["data"])))
            else:
                query = query.order_by(getattr(self.db_object,columns[column_index]["data"]))

        if start is not None and length is not None:
            query = query[start:start+length]

        data = [self.to_dict(c) for c in query]

        recordsTotal = count.first()
        recordsFiltered = count_filtered.first()

        result = {
            "data":data,
            "recordsTotal":recordsTotal,
            "recordsFiltered":recordsFiltered,
            "draw":draw
        }

        return result

    @db_session(serializable=True)
    def get_all_dict(self):
        return [self.to_dict(c) for c in self.db_object.select()]

    @db_session(serializable=True)
    def get_all(self):
        return [c for c in self.db_object.select()]

    @db_session(serializable=True)
    def get(self,id):
        return self.db_object[id]

    @db_session(serializable=True)
    def get_dict(self,id):
        return self.to_dict(self.db_object[id])

    @db_session(serializable=True)
    def delete(self,id):
        object_class = self.db_object[id]
        object_class.delete()

    @db_session(serializable=True)
    def delete_to_dict(self,id):
        object_class = self.db_object[id]
        result = self.to_dict(object_class)
        object_class.delete()
        return result

    @db_session(serializable=True)
    def to_dict(self,obj):
        if obj == None:
            return None
        elif isinstance(obj,list):
            return [self.to_dict(c) for c in obj]
        else:
            return self.db_object[obj.id].to_dict()

