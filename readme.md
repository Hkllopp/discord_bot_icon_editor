# discord_bot_icon_editor

## Installation

1. Clone the project
```bash
git clone https://github.com/Hkllopp/discord_bot_icon_editor
```
2. Go in the directory
```bash
cd discord_bot_icon_editor
```
3. Run the script
```bash
. script.sh
```
4. (If asked) Add your discord bot TOKEN in the .env file
```bash and then rerun the script
nano .env
. script.sh
```

## Specific azure installation

We used systemctl to create a unit file to run the bot as a service. You can find the unit file in the `/etc/systemd/system/discord_bot_icon_editor.service`. You can see the status of the service with the following command:
```bash
systemctl status discord_bot_icon_editor
```