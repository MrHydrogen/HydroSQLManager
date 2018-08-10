from django.db import connection

from hydrosql.sql_commands import COMMANDS


class HydroSqlHandler:
    CREATE_TABLE_COMMAND = COMMANDS["CREATE_TABLE"]
    GET_RECORDS_COMMAND = COMMANDS["GET_RECORDS"]
    GET_RECORD_COMMAND = COMMANDS["GET_RECORD"]
    INSERT_RECORD_COMMAND = COMMANDS["INSERT_RECORD"]
    DELETE_RECORD_COMMAND = COMMANDS["DELETE_RECORD"]
    UPDATE_RECORD_COMMAND = COMMANDS["UPDATE_RECORD"]

    def __init__(self):
        pass

    @classmethod
    def get_tables_name(cls):
        """Returns all tables name"""
        return connection.introspection.table_names()

    def create_table(self, table_name, columns):
        """Create table"""
        joined_columns = ", ".join(columns)

        cursor = connection.cursor()
        command = self.CREATE_TABLE_COMMAND.format(table_name, joined_columns)
        cursor.execute(command)

    def get_records(self, table, limit, offset):
        """Returns records in a table according to limit and offset"""
        cursor = connection.cursor()
        command = self.GET_RECORDS_COMMAND.format(table, limit, offset)
        cursor.execute(command)
        records = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        return self.serialize(records=records, columns=columns, many=True)

    def get_record(self, table, record_id):
        """Returns one record"""
        cursor = connection.cursor()
        command = self.GET_RECORD_COMMAND.format(table, record_id)
        cursor.execute(command)
        columns = [column[0] for column in cursor.description]
        record = cursor.fetchone()
        return self.serialize(records=record, columns=columns)

    def insert_record(self, table, keys, values):
        """Insert a record into table"""
        joined_keys = ", ".join(keys)
        joined_values = ", ".join(map("'{}'".format, values))

        cursor = connection.cursor()
        command = self.INSERT_RECORD_COMMAND.format(table, joined_keys, joined_values)
        cursor.execute(command)

    def delete_record(self, table, record_id):
        """Delete a record from table"""
        cursor = connection.cursor()
        command = self.DELETE_RECORD_COMMAND.format(table, record_id)
        cursor.execute(command)

    def update_record(self, table, record_id, updates):
        """Update a record"""
        joined_updates = ", ".join(updates)

        cursor = connection.cursor()
        command = self.UPDATE_RECORD_COMMAND.format(table, joined_updates, record_id)
        cursor.execute(command)

    @classmethod
    def serialize(cls, records, columns, many=False):
        if not records:
            return None

        if many:
            results = []
            for record in records:
                result = dict(zip(columns, record))
                results.append(result)
            return results
        return dict(zip(columns, records))


class HydroParser:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.keys = []
        self.values = []

    def get_columns(self):
        """Returns columns name in the body"""
        columns = []

        for key, value in self.raw_data.items():
            if key == "table_name":
                continue
            columns.append(key + " " + value)

        return columns

    def set_key_values_from_dict(self):
        """Set keys and values existing in request.data"""
        for key, value in self.raw_data.items():
            self.keys.append(key)
            self.values.append(value)

    def get_updates(self):
        """Returns updates"""
        updates = []
        for key, value in self.raw_data.items():
            updates.append(key + " = " + "'{}'".format(value))
        return updates

    def get_keys(self):
        """Returns keys"""
        return self.keys

    def get_values(self):
        """Return values"""
        return self.values
