name = "psyshort"
import psycopg2, psycopg2.extras, json
from datetime import datetime
from psycopg2.extensions import AsIs
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
    filename="/var/log/psyshort.log",
    level=logging.DEBUG
    )
def log(level="d", message=None):
    level = level.lower()
    levels = {
        "d": {
            "name": "DEBUG",
            "function": logging.debug,
            },
        "i": {
            "name": "INFO",
            "function": logging.info,
            },
        "w": {
            "name": "WARNING",
            "function": logging.warning,
            },
        "e": {
            "name": "ERROR",
            "function": logging.error,
            },
        }
    levels[level]["function"](message)
    print(levels[level]["name"], "psyshort - {msg}".format(msg=message))

class Psyshort():
    def __init__(self, hostname, dbname, username, password):
        self.hostname = hostname
        self.dbname = dbname
        self.username = username
        self.password = password
        self.connect_datetime = self.connect()
        
    def __del__(self):
        self.disconnect()
    
    def connect(self):
        self.conn = psycopg2.connect(
            """dbname='{dbname}'
            user='{user}'
            host='{host}'
            password='{password}'""".format(
                dbname=self.dbname,
                user=self.username,
                host=self.hostname,
                password=self.password
                )
            )
        del self.password, self.username
        return datetime.now()
        
    def disconnect(self):
        self.conn.close()
        return (datetime.now() - self.connect_datetime)
        
    def _check_select_args(self, table, fields, where, limit, order_by):
        assert table
        if fields:
            assert type(fields) == list
        
        if where:
            assert type(where) == str
            
        if limit:
            assert type(limit) == int
            
        if order_by:
            assert type(order_by) == str

    def update(self, table, columns, row):
        with self.conn.cursor() as cur:
            values = []
            for column in columns:
                if type(row[column]) == dict:
                    values.append(json.dumps(row[column]), default=str)
                
                else:
                    values.append(row[column])
                    
            query = "INSERT INTO {table} (%s) VALUES %s".format(table=table)
            try:
                cur.execute(
                    cur.mogrify(
                        query,
                        (
                            AsIs(','.join(columns)),
                            tuple(values)
                            )
                        )
                    )
                
            except psycopg2.IntegrityError as eX:
                if "duplicate key value violates unique constraint" in str(eX):
                    log("d", "UUID already exists: {uuid}".format(uuid=row["uuid"]))

                self.conn.rollback()
                return False
                
            except Exception as eX:
                raise eX
                
            self.conn.commit()
            log("d", "Inserted: {0}.".format(row["uuid"]))
            return True

    def select(self, table, fields=None, where=None, limit=None, order_by=None):
        self._check_select_args(table, fields, where, limit, order_by)
        select_start = datetime.now()
        records = []
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            query = "SELECT"
            if fields:
                query += " ("
                first = True
                for field in fields:
                    if not first:
                        query += ", "
                    
                    first = not first
                    query += "{0}".format(field)
                    
                query += ")"
            
            else:
                query += " *"
            
            query += " FROM {table}".format(table=table)
            if where:
                query += " WHERE {0}".format(where)
                
            if limit:
                query += " LIMIT {0}".format(limit)
                
            if order_by:
                query += " ORDER BY {0}".format(order_by)
                
            try:
                cur.execute(query)
                
            except psycopg2.IntegrityError as eX:
                self.conn.rollback()
                return False
                
            else:
                for row in cur.fetchall():
                    records.append(dict(row))
                    
        return {
            "result": records,
            "duration": (datetime.now() - select_start)
            }
    
    def _check_insert_args(self, table, columns, row):
        assert (
            type(table) == str
            and
            type(columns) == list
            and
            type(row) == dict
            )
    
    def insert(self, table, columns, row):
        with self.conn.cursor() as cur:
            values = []
            for column in columns:
                if type(row[column]) == dict:
                    values.append(json.dumps(row[column]), default=str)
                
                else:
                    values.append(row[column])
                    
            query = "INSERT INTO {table} (%s) VALUES %s".format(table=table)
            try:
                cur.execute(
                    cur.mogrify(
                        query,
                        (
                            AsIs(','.join(columns)),
                            tuple(values)
                            )
                        )
                    )
                
            except psycopg2.IntegrityError as eX:
                if "duplicate key value violates unique constraint" in str(eX):
                    log("d", "UUID already exists: {uuid}".format(uuid=row["uuid"]))

                self.conn.rollback()
                return False
                
            except Exception as eX:
                raise eX
                
            self.conn.commit()
            log("d", "Inserted: {0}.".format(row["uuid"]))
            return True
        
    def insert_multi(self, table, columns, rows):
        insert_start = datetime.now()
        failed_rows = []
        with self.conn.cursor() as cur:
            headers = ", ".join(columns)
            values = [
                tuple(
                    [
                        row[column] for column in columns
                        ]
                    )
                for row in rows
                ]
            query = "INSERT INTO {table} ({headers}) VALUES %s".format(
                table=table,
                headers=headers
                )
            try:
                psycopg2.extras.execute_values(
                    cur=cur,
                    sql=query,
                    argslist=values
                    )
                
            except Exception as eX:
                log("d", eX)
                self.conn.rollback()
                for row in rows:
                    if not self.insert(table, columns, row):
                        failed_rows.append(row)
                        
            self.conn.commit()
            return {
                "failed_rows": failed_rows,
                "duration": (datetime.now() - insert_start),
                }