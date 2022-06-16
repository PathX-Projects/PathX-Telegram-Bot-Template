<div id="top"></div>

<!-- PROJECT LOGO -->
<div align="center">
  <img src="img/telegram_logo.png" alt="Telegram Logo" height="180">
  <h2 align="center"><strong>Telegram Bot Template</strong></h3>
  <p align="center">
    Easily replicate consistent telegram bot structure and functionality with this Telegram bot template.
    <br>
  </p>
  <h3><strong>Features Include:</strong></h3>
  <p align="center" ><i>
    Restricted Access to the Bot Using a Whitelist/Blacklist<br>
    MySQL Database Connection for User Data<br>
    Logger Handles Console and File Logging<br>
  </i></p>
</div>

___

<!-- TABLE OF CONTENTS -->
### Table of Contents
<ol>
    <li><a href="#setup">Setup</a></li>
    <li><a href="#usage">Bot Commands</a></li>
</ol>

<!-- SETUP -->
<div id="setup"></div>

## Setup

1. Ensure that you have Python 3.9+ install on your machine. If not, you can install it [here](https://www.python.org/downloads/release/python-3912/).

2. Add additional functionality to the bot by customizing the [template](bot/telegram_bot.py).

3. Modify the database_schema file to reflect your desired user data/configuration.

4. Add your new commands to [bot_commands.txt](bot_commands.txt).

5. Set config variables in [tg_config.py](bot/tg_config.py) file and [db_config.py](bot/mysql_database/db_config.py) file
   
6. Install  pip packages
   ```bash
   pip install -r requirements.txt
   ``` 

7. Run the Telegram bot from the entrypoint
   ```bash
   python main.py
   ```

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- BOT COMMANDS -->
<div id="usage"></div>

## Bot Commands:

### [View Commands Documentation Here](bot_commands.txt)

<p align="right">(<a href="#top">back to top</a>)</p>