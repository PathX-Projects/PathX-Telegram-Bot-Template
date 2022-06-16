import os

"""----- Database Configuration -----"""
DB_PASSWORD = os.getenv("MYSQL_DB_PASSWORD", "<or-hardcode-here>")
DB_HOST = os.getenv("MYSQL_DB_HOST_IP", "<or-hardcode-here>")
DB_USER = os.getenv("MYSQL_DB_HOST_IP", "root")
DB_NAME = os.getenv("DB_NAME", "<or-hardcode-here>")
DB_TABLE = os.getenv("DB_NAME", "<or-hardcode-here>")  # The table name in the database in which user data is stored


for var in [DB_PASSWORD, DB_HOST, DB_USER, DB_NAME, DB_TABLE]:
    assert var != "<or-hardcode-here>"