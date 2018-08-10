from __future__ import unicode_literals

from django.db import DataError, ProgrammingError
from rest_framework.response import Response

from rest_framework.views import APIView

from .handlers import HydroSqlHandler, HydroParser


class TablesView(APIView):
    def get(self, request):
        """Get all tables name"""
        handler = HydroSqlHandler()
        tables = handler.get_tables_name()
        return Response(tables)

    def post(self, request):
        """Create new table"""
        try:
            table_name = request.data["table_name"]
        except KeyError:
            return Response({"message": "'table_name' field needed"}, status=500)

        parser = HydroParser(request.data)
        columns = parser.get_columns()

        handler = HydroSqlHandler()
        try:
            handler.create_table(table_name, columns)
        except ProgrammingError:
            return Response(status=500)

        return Response()


class RecordsView(APIView):
    def get(self, request, **kwargs):
        """Get records in a table with limit and offset parameters in the query param"""
        table = kwargs["table"]
        offset = request.query_params.get("offset", 0)
        limit = request.query_params.get("limit", 5)

        handler = HydroSqlHandler()
        try:
            records = handler.get_records(
                table=table,
                limit=limit,
                offset=offset
            )
        except ProgrammingError:
            return Response(status=500)

        return Response(records)

    def post(self, request, **kwargs):
        """Create a new record in database"""
        table = kwargs["table"]

        parser = HydroParser(request.data)
        parser.set_key_values_from_dict()
        keys = parser.get_keys()
        values = parser.get_values()

        handler = HydroSqlHandler()
        try:
            handler.insert_record(
                table=table,
                keys=keys,
                values=values
            )
        except (ProgrammingError, DataError):
            return Response(status=500)

        return Response()


class RecordView(APIView):
    """Get a record details"""
    def get(self, request, **kwargs):
        table = kwargs["table"]
        record_id = kwargs["id"]

        handler = HydroSqlHandler()

        try:
            record = handler.get_record(
                table=table,
                record_id=record_id
            )
        except ProgrammingError:
            return Response(status=500)

        return Response(record)

    def put(self, request, **kwargs):
        """Update an existing record"""
        table = kwargs["table"]
        record_id = kwargs["id"]

        parser = HydroParser(request.data)
        updates = parser.get_updates()

        if not updates:
            return Response({"message": "nothing to update !"}, status=500)

        handler = HydroSqlHandler()
        try:
            handler.update_record(
                table=table,
                record_id=record_id,
                updates=updates
            )
        except ProgrammingError:
            return Response(status=500)

        return Response()

    def delete(self, request, **kwargs):
        """Delete a record"""
        table = kwargs["table"]
        record_id = kwargs["id"]

        handler = HydroSqlHandler()
        try:
            handler.delete_record(
                table=table,
                record_id=record_id
            )
        except ProgrammingError:
            return Response(status=500)

        return Response()
