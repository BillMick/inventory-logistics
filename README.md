# inventory-logistics
Python based app to manage inventory and logistics

# To begin
## Database settings
For this app, we use __postgreSQL__. 
1. So ensure to have it installed at your convenience (with or not GUI) according to your OS.
2. Create the database __inventory_logistics__.
    - If you are using terminal on linux OS (debian for example):
        - connect to your Postgres:
        ```bash
        psql -U postgres -h 127.0.0.1
        ```
        - Create your database:
        ```bash
        CREATE DATABASE inventory_logistics;
        ```
        - Verify the existence of your database:
        ```bash
        \l;
        ```
        > If all has gone well, you should see in the list your new database.
    - If you are using windows OS with GUI like PgAdmin, you can create graphically your database.
3. Run the `first_usage.py` file to create tables.