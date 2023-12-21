# Roblox E KITTEN Notifier

## Overview

Roblox E KITTEN Notifier is a Python script that allows you to monitor a Roblox user's activity in real-time and receive notifications on a Discord channel when specific events occur. This script can help you keep track of various aspects of a Roblox user's activity, including display name changes, friend additions/removals, group joins/leaves, follower changes, presence status, and the acquisition of new badges.

## Features

- **Real-Time Monitoring**: This script offers real-time monitoring of a Roblox user's activity.

- **User Activity Tracking**: Keep track of a user's Roblox activity, including display name changes, friend interactions, group affiliations, follower changes, presence status, and badge acquisitions.

- **Flexible Configuration**: Easily configure the script by providing your Roblox username, Discord webhook URL, and Roblox security token.

- **Webhook Integration**: Notifications are sent to a Discord channel of your choice using webhooks. You can customize the format and appearance of the notifications as needed.

## Usage

1. **Setup Roblox Security Token**: Obtain your Roblox security token. Guides are available online on how to do this. Set your Roblox security token in the script by replacing the `security_token` variable value with your token.

2. **Configure Discord Webhook**: Create a Discord webhook for the channel where you want to receive notifications. Guides on creating webhooks in Discord can be found online. Set the `webhook_url` variable value in the script to your Discord webhook URL.

3. **Run the Script**: Execute the script with Python. Ensure you have the necessary dependencies installed. The script will continuously monitor your Roblox account and send notifications to your Discord channel when relevant events occur.

4. **Customize Notifications (Optional)**: Customize the notifications sent to your Discord channel by modifying the `post_to_webhook` function in the script. Adjust the notification content and format to your preference.

## Dependencies

- This script relies on the `requests` library to interact with the Roblox API and send notifications to Discord. You can install it using `pip`:

   ```bash
   pip install requests
