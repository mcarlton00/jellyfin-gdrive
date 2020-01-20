# Jellyfin GDrive

## Overview

This script acts in place of inotify when using Google Drive and rclone as a backend for Jellyfin.  It watches the Drive API and will trigger a library scan on changes

## Notes

Currently only works when adding new files

Requires Python 3.6 or newer

# Installation

1. Download repo
2. Install Python dependencies
    * `pip install -r requirements.txt`
3. Edit `config.json`
4. Follow step 1 of Google's [getting started](https://developers.google.com/drive/api/v3/quickstart/python) page
    * Save the credentials.json file inside the project directory
6. `python scanner.py` - to run the script

# Configuration

- `check_interval` - minutes between GDrive scans
- `api_key` - Jellyfin API Key (Admin Dashboard -> Advanced -> API Keys)
- `jellyfin_server` - URL of the Jellyfin server (`http://localhost:8096`)
- `retries` - number of tries for Jellyfin api before giving up
