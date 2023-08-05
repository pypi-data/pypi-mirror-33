Making psycopg2 a little simpler to use.

Usage:
```python
from psyshort import Psyshort
psy = Psyshort(
    hostname="db.example.com",
    dbname="example_database",
    username="postgres_user",
    password="pa$$w0rd"
    )
select = psy.select(
    table="my_table", # Table's name (mandatory).
    fields=[
        "id",
        "first_name",
        "last_name",
        "phone",
        ], # Fields to include in the result (optional).
    where="last_name = 'Smith'", # Select only rows where last_name = 'Smith' applies (optional).
    limit=1000, # Limit result to 1000 records (optional).
    order_by="first_name" # Order the result by 'first_name' column (optional).
    )
result = select["result"] # The selected records.
duration = select["duration"] # The duration of the operation.
    
psy.insert(
    table="my_table", # Table's name (mandatory).
    columns=[
        "first_name",
        "last_name",
        "phone",
        ], # Columns by which to insert values (mandatory).
    row={
        "first_name": "John",
        "last_name": "Smith",
        "phone": "KL5-2390"
        } # Row to insert to the table (mandatory).
    )
    
psy.disconnect() # Occurs on psy.__del__
```