from os import getenv

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, ARRAY, BIGINT, BigInteger, BINARY, BLOB, Boolean, CHAR, CLOB, Date, \
    DateTime, DECIMAL, Enum, Float, Integer, Interval, JSON, LargeBinary, NCHAR, Numeric, NVARCHAR, PickleType, REAL, \
    SmallInteger, String, Text, Time, TIMESTAMP, TypeDecorator, Unicode, UnicodeText, VARBINARY, VARCHAR
from sqlalchemy.dialects.oracle import RAW, VARCHAR2
from sqlalchemy import inspect

BASE = declarative_base()


class DB:
    def __init__(self, session=None):
        self.session = session
        self.connection = None

    def _connection(self, environment, name):
        engine = None
        environment[name]['USER'] = getenv(f"DB_USER_{name.upper()}")
        environment[name]['PASSWORD'] = getenv(f"DB_PASSWORD_{name.upper()}")

        if environment[name]['DB_TYPE'].lower() == 'postgresql':
            engine = create_engine(f"postgresql://{environment[name]['USER']}:{environment[name]['PASSWORD']}@"
                                   f"{environment[name]['HOST']}:{environment[name]['PORT']}/"
                                   f"{environment[name]['DB_NAME']}")
        elif environment[name]['DB_TYPE'].lower() == 'mysql':
            engine = create_engine(
                f"mysql://{environment[name]['USER']}:{environment[name]['PASSWORD']}@{environment[name]['HOST']}/"
                f"{environment[name]['DB_NAME']}")
        elif environment[name]['DB_TYPE'].lower() == 'oracle_as_sysdba':
            engine = create_engine(
                f"oracle://{environment[name]['USER']}:{environment[name]['PASSWORD']}@{environment[name]['HOST']}:"
                f"{environment[name]['PORT']}/?service_name={environment[name]['DB_NAME']}&mode=2"
            )
        elif environment[name]['DB_TYPE'].lower() == 'oracle_as_normal':
            engine = create_engine(
                f"oracle://{environment[name]['USER']}:{environment[name]['PASSWORD']}@{environment[name]['HOST']}:"
                f"{environment[name]['PORT']}/?service_name={environment[name]['DB_NAME']}"
            )
        elif environment[name]['DB_TYPE'].lower() == 'mssql':
            engine = create_engine(f"mssql+pyodbc://{environment[name]['USER']}:{environment[name]['PASSWORD']}@"
                                   f"{environment[name]['DB_NAME']}")
        elif environment[name]['DB_TYPE'].lower() == 'sqlite':
            engine = create_engine(f"sqlite:///{environment[name]['PATH']}")

        return engine

    def create_session(self, environment, name):
        self.connection = self._connection(environment=environment, name=name)
        Session = sessionmaker(self.connection)
        if environment[name]['DB_TYPE'].lower() != 'postgresql':
            BASE.metadata.create_all(self.connection)
        return Session()

    def get(self, table_name: any, limit: int = 0, offset: int = 0):
        try:
            if limit and not offset:
                result = self.session.query(table_name).limit(limit).all()
            elif limit and offset:
                result = self.session.query(table_name).limit(limit).offset(offset).all()
            else:
                result = self.session.query(table_name).all()
            items = []
            for row in result:
                tmp = {}
                for _row in vars(row):
                    if _row not in ['_sa_instance_state']:
                        tmp[_row] = row.__dict__[_row]
                items.append(tmp)
            return items
        except BaseException as e:
            print(e.args)
            return False

    def create(self, query_object: any):
        try:
            self.session.add(query_object)
            self.session.commit()
            return {'id': query_object.id}
        except BaseException as e:
            print(e.args)
            self.session.rollback()
            return False

    def create_all(self, query_object: any):
        try:
            self.session.add_all(query_object)
            self.session.commit()
            ids = []
            for item in query_object:
                ids.append(item.id)
            return {'ids': ids}
        except BaseException as e:
            print(e.args)
            self.session.rollback()
            return False

    def update(self, table_name: any, condition: dict, update_value: dict):
        try:
            self.session.query(table_name).filter_by(**condition).update(update_value)
            self.session.commit()
            return 'Successful updated'
        except BaseException as e:
            print(e.args)
            self.session.rollback()
            return False

    def delete(self, table_name: any, condition: dict):
        try:
            self.session.query(table_name).filter_by(**condition).delete()
            self.session.commit()
            return 'Successful deleted'
        except BaseException as e:
            print(e.args)
            self.session.rollback()
            return False

    def execute(self, query: str):
        """
            execute("SELECT * FROM user WHERE id=5")
            :param query: str
            :return:
        """
        try:
            result = self.session.execute(query)
            self.session.commit()
            items = []
            for row in result:
                items.append(row)
            return items
        except BaseException as e:
            print(e.args)
            self.session.rollback()
            return False

    def get_by(self, table_name: any, condition: dict, limit: int = 0, offset: int = 0):
        try:
            if limit and not offset:
                result = self.session.query(table_name).filter_by(**condition).limit(limit).all()
            elif limit and offset:
                result = self.session.query(table_name).filter_by(**condition).limit(limit).offset(offset).all()
            else:
                result = self.session.query(table_name).filter_by(**condition).all()
            items = []

            def object_as_dict(obj):
                return {c.key: getattr(obj, c.key)
                        for c in inspect(obj).mapper.column_attrs}

            for i in result:
                items.append(object_as_dict(i))
            return items
        except BaseException as e:
            print(e.args)
            return False

    def get_columns_by_filter(self, table_name: any, filter_expession: any, columns: [str] = None):
        try:
            if columns:
                query = self.session.query(table_name).with_entities(*[Column(x) for x in columns])
            else:
                query = self.session.query(table_name)

            result = query.filter(filter_expession).all()

            items = []

            for i in result:
                items.append(dict(zip(columns, i)))
            return items
        except BaseException as e:
            print(e.args)
            return False

    def get_by_id(self, table: any, row_id: int or str):
        """
        get row from DB by ID
        :param table: table model
        :param row_id: primary key
        :return: row
        """
        try:
            result = self.session.query(table).get(row_id)

            def object_as_dict(obj):
                return {c.key: getattr(obj, c.key)
                        for c in inspect(obj).mapper.column_attrs}

            return object_as_dict(result)
        except BaseException as e:
            print(e.args)
            return False

    def close(self):
        self.session.close()
        self.connection.dispose()


class DBHelper:
    def column(self, column, dimensions=1, *args, **kwargs):
        """
        :param column:
            array, biging, giginteger, binary,
            blob, bool, char, clob, date,
            datetime, decimal, emum, float,
            int, interval, json, largebinary,
            nchar, numeric, nvarchar, pickletype,
            real, smallint, str, text, time,
            timestamp, typedecoder, unicode,
            unicodetext, varbinary, varchar
        :param dimensions: 1
        :return: поле типа SQL
        """
        column_type = {
            'array': ARRAY,
            'biging': BIGINT,
            'giginteger': BigInteger,
            'binary': BINARY,
            'blob': BLOB,
            'bool': Boolean,
            'char': CHAR,
            'clob': CLOB,
            'date': Date,
            'datetime': DateTime,
            'decimal': DECIMAL,
            'emum': Enum,
            'float': Float(dimensions),
            'int': Integer,
            'interval': Interval,
            'json': JSON,
            'largebinary': LargeBinary,
            'nchar': NCHAR,
            'numeric': Numeric,
            'nvarchar': NVARCHAR,
            'pickletype': PickleType,
            'real': REAL,
            'smallint': SmallInteger,
            'str': String(dimensions),
            'text': Text(dimensions),
            'time': Time,
            'timestamp': TIMESTAMP,
            'typedecoder': TypeDecorator,
            'unicode': Unicode,
            'unicodetext': UnicodeText,
            'varbinary': VARBINARY,
            'varchar': VARCHAR(dimensions),
            'varchar2': VARCHAR2(dimensions),
            'raw': RAW(dimensions),
        }.get(column, 'varchar')

        return Column(column_type, *args, **kwargs)
