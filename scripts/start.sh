#!/bin/bash

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

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
    if [ -f ".env.sample" ]; then
        CMP_OUTPUT=$(cmp ".env" ".env.sample" 2>&1)
        CMP_STATUS=$?
        
        case $CMP_STATUS in
            0) echo "Your .env is identical to .env.sample"
               echo "Please edit .env and add your Discord token"
               exit 1 ;;
            1) echo "Configuration appears to be set. Continuing..." ;;
            2) echo "Error comparing files. Please check file permissions."
               echo "Error details: $CMP_OUTPUT"
               exit 2 ;;
        esac
    fi
fi

# Check if venv directory exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    
    # Activate venv and install requirements
    source venv/bin/activate
    if [ -f "requirements.txt" ]; then
        echo "Installing requirements..."
        python3 -m pip install -r requirements.txt
    else
        echo "Warning: requirements.txt not found"
    fi
else
    echo "Virtual environment found"
    source venv/bin/activate
fi

# Start the bot
python3 bot.py
