#!/bin/bash

# Prompt for user input
read -p "Enter your address: " SN_ADDRESS
read -p "Enter your default timezone: " SN_DEFAULT_TIMEZONE

# Export the variable
export SN_ADDRESS
export SN_DEFAULT_TIMEZONE

# Run docker-compose
docker-compose up