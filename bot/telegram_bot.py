import os
import time

from .tg_config import *
from ._logger import logger
from .io_handler import get_temp_dir, create_zip_archive, walk_dir, clr_temp_dir, get_administrators, get_logfile
from .mysql_database.database_handler import DatabaseHandler

from telebot import TeleBot
from requests.exceptions import ReadTimeout
from mysql.connector.errors import DatabaseError


class TelebotTemplate(TeleBot):
    def __init__(self):
        super().__init__(token=TELEGRAM_BOT_TOKEN)

        self.db_client = DatabaseHandler()
        logger.info(f'{self.get_me().first_name} initialized')

        @self.message_handler(commands=['help'])
        @self.user_is_whitelisted
        def on_help(message):
            self.reply_to(message, f'View the documentation for the bot here:\n{EXTERNAL_DOCUMENTATION_LINK}')

        @self.message_handler(commands=['viewconfig'])
        @self.user_is_whitelisted
        def on_viewconfig(message):
            """Returns the current configuration of the bot (used as reference for /setconfig)"""
            try:
                config = self.db_client.pull_user_config(user_id=message.from_user.id)
                msg = f"{message.from_user.username} {self.get_me().first_name} Configuration:\n\n"
                for k, v in config.items():
                    # msg += f"{key.strip()} settings:\n"
                    # for k, v in variables.items():
                    msg += f'{k}={v}\n'
                    # msg += '\n'
                self.reply_to(message, msg)

            except Exception as exc:
                logger.exception('Could not call /viewconfig', exc_info=exc)
                self.reply_to(message, str(exc))

        @self.message_handler(commands=['setconfig'])
        @self.user_is_whitelisted
        def on_setconfig(message):
            """Used to change configuration variables of the bot"""
            msg = ""
            failed = []
            user_id = message.from_user.id
            config = self.db_client.pull_user_config(user_id)
            try:
                for change in self.split_message(message.text):
                    try:
                        conf, val = change.split('=')

                        # Account for bool case:
                        if val.lower() == 'true' or val.lower() == 'false':
                            val = val.lower() == 'true'

                        try:
                            var_type = type(config[conf])
                        except KeyError:
                            raise KeyError(f"{conf} does not match any available config settings in database.")

                        # Attempt to push the config update to the database:
                        self.db_client.update_user_config(user_id=user_id, config_name=conf,
                                                          new_value=var_type(val))

                        msg += f"{conf} set to {val}\n"
                        logger.info(f"{user_id}: {conf} set to {val} ({var_type})\n")
                    except Exception as exc:
                        failed.append((change, str(exc)))
                        continue

                if len(msg) > 0:
                    self.reply_to(message, "Successfully set configuration:\n\n" + msg)

                if len(failed) > 0:
                    fail_msg = "Failed to set:\n\n"
                    for fail in failed:
                        fail_msg += f"- {fail[0]} (Error: {fail[1]})\n"
                    self.reply_to(message, fail_msg)
            except Exception as exc:
                logger.exception('Could not set config', exc_info=exc)
                self.reply_to(message, str(exc))

        @self.message_handler(commands=['whitelist'])
        @self.user_is_administrator
        def on_whitelist(message):
            """Used to change configuration variables of the bot"""
            try:
                splt_msg = self.split_message(message.text)
                if len(splt_msg) > 0:
                    new_users = splt_msg[0].split(",")
                    for user in new_users:
                        self.db_client.whitelist_user(user)
                    self.reply_to(message, f'Whitelisted: {new_users}')
                    logger.info(f'Whitelisted: {new_users}')
                else:
                    msg = f"{self.get_me().full_name} Whitelist:\n"
                    for user in self.db_client.load_whitelist():
                        msg += f"- {user}\n"
                    self.reply_to(message, msg)
            except Exception as exc:
                self.reply_to(message, str(exc))

        @self.message_handler(commands=['restartbot'])
        @self.user_is_administrator
        def on_restartbot(message):
            self.reply_to(message, f'Bot restarting - '
                                   f'Please wait {ERROR_RESTART_DELAY} seconds')
            raise Exception("Bot restart called")

        @self.message_handler(commands=['getlogs'])
        @self.user_is_administrator
        def on_getlogs(message):
            self.reply_to(message, f'Fetching logfile...')
            self.send_document(message.chat.id, open(get_logfile(), 'rb'))

    def split_message(self, message, convert_type=None) -> list:
        if convert_type is None:
            return [chunk.strip() for chunk in message.split(" ")[1:] if
                    not all(char == " " for char in chunk) and len(chunk) > 0]
        else:
            return [convert_type(chunk.strip()) for chunk in message.split(" ")[1:] if
                    not all(char == " " for char in chunk) and len(chunk) > 0]

    def user_is_whitelisted(self, func):
        """
        (Decorator) Checks if the user is whitelisted before proceeding with the function
        
        :param func: Expects the function to be a message handler, with the 'message' class as the first argument 
        """

        def wrapper(*args, **kw):
            message = args[0]
            user_id = str(message.from_user.id)
            if user_id in self.db_client.load_whitelist():
                return func(*args, **kw)
            else:
                self.reply_to(message, f"{message.from_user.username} is not whitelisted.\n"
                                       f"Please send your user ID ({user_id}) the developer: {DEVELOPER_CONTACT}")
                return False

        return wrapper

    def user_is_administrator(self, func):
        """
        (Decorator) Checks if the user is an administrator before proceeding with the function

        :param func: Expects the function to be a message handler, with the 'message' class as the first argument
        """

        def wrapper(*args, **kw):
            message = args[0]
            user_id = str(message.from_user.id)
            if user_id in get_administrators():
                return func(*args, **kw)
            else:
                self.reply_to(message,
                              f"{message.from_user.username} ({message.from_user.id}) is not an administrator.")
                return False

        return wrapper

    def alert_users(self, message: str) -> None:
        for user in self.db_client.load_whitelist():
            self.send_message(chat_id=user, text=message)

    def alert_admins(self, message: str) -> None:
        for user in get_administrators():
            self.send_message(chat_id=user, text=message)

    def run_bot(self):
        while True:
            try:
                logger.info("Bot started")
                # Poll for changes
                self.polling()
            except ReadTimeout:
                err_msg = f'Bot has crashed due to read timeout - restarting in {ERROR_RESTART_DELAY} seconds...'
                logger.error(err_msg)
                self.alert_admins(err_msg)
                time.sleep(ERROR_RESTART_DELAY)
            except DatabaseError as exc:
                logger.exception(f'MySQL error has occurred', exc_info=exc)
                self.alert_admins(f'A critical database error has occurred:\n{exc}')
                break
            except KeyboardInterrupt:
                logger.info("Bot stopping for keyboard interrupt...")
                break
            except Exception as exc:
                logger.exception(f'Bot has unexpectedly crashed - restarting in {ERROR_RESTART_DELAY}:', exc_info=exc)
                self.alert_admins(f'Bot has unexpectedly crashed - Error {exc}')
                time.sleep(ERROR_RESTART_DELAY)
