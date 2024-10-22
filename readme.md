# discord_bot_icon_editor

## Installation

1. Clone the project
```bash
git clone https://github.com/Hkllopp/discord_bot_icon_editor
```
2. Create a virtual environment
```bash
python -m venv venv
```
3. Activate the virtual environment
```bash
# Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```
4. Install the requirements
```bash
pip install -r requirements.txt
# If installation fails, you can try to install the requirements one by one using the light_requirements.txt file
```
5. Create a credentials file using .env.sample as a template (and use your own secrets). You can find a guid to create a discord bot [here](https://discordpy.readthedocs.io/en/stable/discord.html)
```bash
cp .env.sample .env
```
6. Run the bot
```bash
python bot.py
```