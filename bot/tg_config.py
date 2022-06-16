import os

"""----- TELEGRAM CONFIGURATION -----"""
TELEGRAM_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "<or-hardcode-here>")
ERROR_RESTART_DELAY = 5  # In seconds
EXTERNAL_DOCUMENTATION_LINK = "<insert_external_documentation_link_here>"
DEVELOPER_CONTACT = "<insert_developer_contact_here>"


assert TELEGRAM_BOT_TOKEN != "<or-hardcode-here>"