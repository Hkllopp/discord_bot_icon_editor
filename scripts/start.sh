#!/bin/bash

# Check if .env exists and handle it
if [ ! -f ".env" ]; then
    if [ -f ".env.sample" ]; then
        echo "Creating .env from template..."
        cp .env.sample .env
        echo "Please edit .env and add your Discord token"
        exit 1
    else
        echo "Error: .env.sample not found"
        exit 1
    fi
else
    # Compare .env with .env.sample
    if [ -f ".env.sample" ] && ! cmp -s ".env" ".env.sample"; then
        echo "Your credentials aren't set in the .env file."
        echo "Please ensure you have set your Discord token"
        exit 1
    fi
fi

# Check if venv directory exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python -m venv venv
    
    # Activate venv and install requirements
    source ./venv/Scripts/activate
    if [ -f "requirements.txt" ]; then
        echo "Installing requirements..."
        pip install -r requirements.txt
    else
        echo "Warning: requirements.txt not found"
    fi
else
    echo "Virtual environment found"
    source ./venv/Scripts/activate
fi

# Start the bot
python ./bot.py