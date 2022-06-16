"""Use this example scheme structure to create a new table in the database or append new rows when a user is whitelisted"""

DATABASE_SCHEMA = {
    "TABLE_NAME": "Users",
    "COLUMNS": [
        dict(column_name="user_id", datatype="TINYTEXT", default_value="{}"),  # To be formatted to Telegram user ID
        dict(column_name="contract_type", datatype="TINYTEXT", default_value="'option'"),
        dict(column_name="loop_count", datatype="INT(10)", default_value="10000"),
        dict(column_name="max_qty", datatype="INT(10)", default_value="4"),
        dict(column_name="target_price_interval_add", datatype="FLOAT(6)", default_value="0.01"),
        dict(column_name="result_price_interval_start", datatype="FLOAT(6)", default_value="-0.4"),
        dict(column_name="result_price_interval_add", datatype="FLOAT(6)", default_value="0.01"),
        dict(column_name="result_price_interval_end", datatype="FLOAT(6)", default_value="0.4"),
        dict(column_name="strike_percentage", datatype="FLOAT(6)", default_value="0.05"),
        dict(column_name="zip_output", datatype="BIT(1)", default_value="0"),
        dict(column_name="option_data_source", datatype="TINYTEXT", default_value="'dex'"),
    ]
}

# To add settings, add a new dict constructor to the end of the "COLUMNS" list

# BIT(1) datatype columns are currently presumed to be boolean values, with 1 == True and 0 == False
