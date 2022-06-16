import time
from time import sleep
from typing import Optional

import mysql.connector

from .db_config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from .database_schema import DATABASE_SCHEMA


class DatabaseHandler:
    def __init__(self):
        self.db = None
        self.cursor = None
        self.initialize_connection()

    def initialize_connection(self, _try: int = 1, exc: Exception = None):
        max_retries = 5
        connection_delay = 2  # In seconds
        if _try > max_retries:
            raise mysql.connector.DatabaseError(f"Could not connect to MySQL database after {max_retries} retries"
                                                f"{f' - Error: {exc}' if exc is not None else ''}")
        try:
            try:
                self.close()
            except:
                pass
            finally:
                self.db = mysql.connector.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME
                )
                self.cursor = self.db.cursor()
        except Exception as exc:
            sleep(connection_delay)  # Connection delay
            self.initialize_connection(_try + 1, exc=exc)

    def create_default_table(self):
        if not self.db.is_connected():
            self.initialize_connection()

        columns = ", ".join([f"{column['column_name']} {column['datatype']}" for column in DATABASE_SCHEMA["COLUMNS"]])
        self.cursor.execute(f"CREATE TABLE {DATABASE_SCHEMA['TABLE_NAME']} ({columns})")

    def load_whitelist(self) -> list[str]:
        """
        Loads all whitelisted users from the database

        :return: List of dictionaries that show: {"id": id, "is_admin": True/False}
        """
        if not self.db.is_connected():
            self.initialize_connection()

        self.cursor.execute(f"SELECT user_id FROM {DATABASE_SCHEMA['TABLE_NAME']}")
        return [user[0] for user in self.cursor]

    def whitelist_user(self, user_id: str):
        """
        Adds a new user to the database.

        :param user_id: Telegram user ID (numerical string not their username)
        :param is_admin: Identifies whether or not the user has admin permissions.
        """
        if not self.db.is_connected():
            self.initialize_connection()

        if user_id in self.load_whitelist():
            raise AssertionError(f"User ({user_id}) is already whitelisted.")

        # Build default values query string
        values = ", ".join([column["default_value"] for column in DATABASE_SCHEMA["COLUMNS"]]).format(user_id)

        self.cursor.execute(f"INSERT INTO {DATABASE_SCHEMA['TABLE_NAME']} VALUES ({values})")
        self.db.commit()

    def blacklist_user(self, user_id: str):
        if not self.db.is_connected():
            self.initialize_connection()

        if user_id not in self.load_whitelist():
            raise AssertionError(f"User ({user_id}) is not on the whitelist.")

        self.cursor.execute(f"DELETE FROM {DATABASE_SCHEMA['TABLE_NAME']} WHERE user_id = {user_id}")
        self.db.commit()

    def pull_user_config(self, user_id: str) -> dict:
        """
        :param user_id: Telegram user ID
        :return: The current user configuration for the Bot
                 NOTE: Boolean values will be represented as 1 = True, 0 = False
        """
        if not self.db.is_connected():
            self.initialize_connection()

        self.cursor.execute(f"SELECT * FROM {DATABASE_SCHEMA['TABLE_NAME']} WHERE user_id = {user_id}")
        try:
            config = [user for user in self.cursor][0]
        except IndexError:
            raise IndexError(f"User ({user_id}) not found in database.")

        return {col[0]: val if 'bit(1)' not in str(col[1]).lower() else val == 1 for col, val in
                zip(self.get_table_columns(), config)}

    def update_user_config(self, user_id: str, config_name: str, new_value) -> dict:
        """
        Updates config settings in the database for the given user.

        :param user_id: Telegram user ID
        :param config_name: Config column name (exact)
        :param new_value: New value for the config column - Variable types
        :return: The updated user config for the given user_id
                 NOTE: Bools will be represented as 1 = True, 0 = False
        """
        if not self.db.is_connected():
            self.initialize_connection()

        if type(new_value) is str:
            # Enclose strings in single quotes to avoid errors
            new_value = f"'{new_value}'"
        elif type(new_value) is bool:
            new_value = 1 if new_value else 0
        self.cursor.execute(f"UPDATE {DATABASE_SCHEMA['TABLE_NAME']} SET {config_name} = {new_value} WHERE user_id = {user_id}")
        self.cursor.execute("COMMIT")

        return self.pull_user_config(user_id)

    def get_table_columns(self) -> list[tuple]:
        """Returns the ordered names of all table columns"""
        if not self.db.is_connected():
            self.initialize_connection()

        self.cursor.execute(f"DESCRIBE {DATABASE_SCHEMA['TABLE_NAME']}")
        return [(col[0], col[1]) for col in self.cursor]

    """----- UTIL/DEBUG FUNCTIONS BELOW -----"""
    def view_table_entries(self, table_name: str):
        if not self.db.is_connected():
            self.initialize_connection()

        self.cursor.execute(f"SELECT * FROM {table_name}")
        for x in self.cursor:
            print(x)

    def describe_table(self, table_name: str):
        if not self.db.is_connected():
            self.initialize_connection()

        self.cursor.execute(f"DESCRIBE {table_name}")
        for x in self.cursor:
            print(x)

    def show_databases(self):
        """Used for debugging"""
        if not self.db.is_connected():
            self.initialize_connection()

        self.cursor.execute("SHOW DATABASES")
        for x in self.cursor:
            print(x)

    def remove_table(self, table_name: str):
        if not self.db.is_connected():
            self.initialize_connection()

        self.cursor.execute(f"DROP TABLE {table_name}")

    def add_column(self, column_name: str, data_type: str, default_value: Optional):
        """
        :param column_name: The name of the new column
        :param data_type: The MySQL datatype (case sensitive) for entries in the new column
        :param default_value: The default value for entries in the new column (wrap strings in single quotes)
        """
        self.cursor.execute(f"ALTER TABLE {DATABASE_SCHEMA['TABLE_NAME']} "
                            f"ADD COLUMN {column_name} {data_type} NOT NULL")
        self.set_column_values(column_name, default_value)

    def remove_column(self, column_name: str):
        self.cursor.execute(f"ALTER TABLE {DATABASE_SCHEMA['TABLE_NAME']} DROP COLUMN {column_name}")

    def set_column_values(self, column_name: str, value: Optional):
        self.cursor.execute(f"UPDATE {DATABASE_SCHEMA['TABLE_NAME']} SET {column_name} = {value}")
        self.cursor.execute("COMMIT")

    def close(self):
        self.cursor.close()
