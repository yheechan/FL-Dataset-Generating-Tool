import psycopg2

class Database:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        self.db = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.database
        )
        self.cursor = self.db.cursor()
    
    def __del__(self):
        self.db.close()
        self.cursor.close()
    
    def execute(self, query, args={}):
        self.cursor.execute(query, args)
        return self.cursor.fetchall()
    
    def commit(self):
        self.db.commit()


class CRUD(Database):
    def __init__(self, host, port, user, password, database):
        super().__init__(host, port, user, password, database)

    # CRUD FUNCTIONS
    def create_table(self, table_name, columns):
        """
        Create a table with explicit locking to prevent deadlocks.
        """
        try:
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            self.cursor.execute(query)
            self.commit()
        except psycopg2.errors.DeadlockDetected as e:
            print(f"Deadlock detected while creating table '{table_name}': {e}")
            self.db.rollback()
        except Exception as e:
            print(f"Error creating table: {e}")
            self.db.rollback()
    
    def create_index(self, table_name, index_name, columns):
        """
        Create an index on a table with explicit locking to prevent deadlocks.
        """
        try:
            query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})"
            self.cursor.execute(query)
            self.commit()
        except psycopg2.errors.DeadlockDetected as e:
            print(f"Deadlock detected while creating index '{index_name}' on table '{table_name}': {e}")
            self.db.rollback()
        except Exception as e:
            print(f"Error creating index: {e}")
            self.db.rollback()

    def drop_table(self, table_name):
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.cursor.execute(query)
        self.commit()

    def insert(self, table_name, columns, values):
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        self.cursor.execute(query)
        self.commit()

    def read(self, table_name, columns="*", conditions={}, special=""):
        query = f"SELECT {columns} FROM {table_name}"
        if conditions:
            condition_clause = " AND ".join([f"{col} = %s" for col in conditions.keys()])
            query += f" WHERE {condition_clause}"
            values = list(conditions.values())
        else:
            values = []
        if special != "":
            query += f" {special}"
        return self.execute(query, values)

    def update(self, table_name, set_values={}, conditions={}, special=""):
        """
        Update method for database.
        
        :param table: str, the name of the table
        :param set_values: dict, column-value pairs to update
        :param conditions: dict, column-value pairs for WHERE clause
        """
        set_clause = ", ".join([f"{col} = %s" for col in set_values.keys()])
        query = f"UPDATE {table_name} SET {set_clause}"
        
        values = list(set_values.values())
        
        if conditions:
            condition_clause = " AND ".join([f"{col} = %s" for col in conditions.keys()])
            query += f" WHERE {condition_clause}"
            values += list(conditions.values())
        
        if special != "":
            query += f" {special}"
        
        print(query, values)
        
        self.cursor.execute(query, values)
        self.commit()

    def delete(self, table_name, conditions={}):
        condition_clause = " AND ".join([f"{col} = %s" for col in conditions.keys()])
        query = f"DELETE FROM {table_name} WHERE {condition_clause}"
        values = list(conditions.values())
        self.cursor.execute(query, values)
        self.commit()


    def add_column(self, table_name, column_definition):
        """
        Add a new column to an existing table after checking its existence.
        """
        try:
            self.cursor.execute(f"LOCK TABLE {table_name} IN ACCESS EXCLUSIVE MODE")
            query = f"ALTER TABLE {table_name} ADD COLUMN {column_definition}"
            self.cursor.execute(query)
            self.commit()
        except psycopg2.errors.DeadlockDetected as e:
            print(f"Deadlock detected while adding column to table '{table_name}': {e}")
            self.db.rollback()
        except Exception as e:
            print(f"Error adding column: {e}")
            self.db.rollback()

    # HELPER FUNCTIONS
    def table_exists(self, table_name):
        """
        Check if table exists in the database
        returns True if exists, False otherwise
        """
        query = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')"
        result = self.execute(query)
        return result[0][0]

    def column_exists(self, table_name, column_name):
        """
        Check if a column exists in a table
        returns 1 if exists, 0 otherwise
        """
        query = f"""
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='{table_name}' 
            AND column_name='{column_name}'
        )
        """
        result = self.execute(query)
        return 1 if result[0][0] else 0
    
    def value_exists(self, table_name, conditions={}):
        """
        Check if a value exists in a column based on given conditions
        returns 1 if exists, 0 otherwise
        """
        condition_clause = " AND ".join([f"{col} = %s" for col in conditions.keys()])
        query = f"SELECT EXISTS (SELECT 1 FROM {table_name} WHERE {condition_clause})"
        values = list(conditions.values())
        result = self.execute(query, values)
        return 1 if result[0][0] else 0