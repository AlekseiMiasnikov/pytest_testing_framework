from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID

from core.db.db import DB, DBHelper, BASE

db = DBHelper()


class ModelExample(DB, BASE):
    __tablename__ = 'example_table'
    __table_args__ = {'schema': 'example_table'}

    id_example = db.column(column='int', primary_key=True)
    date_example = db.column(column='date')
    name_example = db.column(column='str')
    guid_example = Column(UUID(as_uuid=True), default=uuid4)

    def __init__(self, session, data=None):
        super().__init__(session)
        self.id_example = data['id_example'] if data is not None else ''
        self.date_example = data['date_example'] if data is not None else ''
        self.name_example = data['name_example'] if data is not None else ''
        self.guid_example = data['guid_example'] if data is not None else ''

    def get_example(self):
        return self.get(table_name=ModelExample)

    def add_exampleg(self, query):
        return self.create(query_object=query)

    def add_example(self, query):
        return self.create_all(query_object=query)

    def update_example(self, condition, update_value):
        return self.update(table_name=ModelExample, condition=condition, update_value=update_value)

    def delete_example(self, condition):
        return self.delete(table_name=ModelExample, condition=condition)

    def execute_example(self, query):
        return self.execute(query=query)

    def get_example_by(self, condition):
        return self.get_by(table_name=ModelExample, condition=condition)
