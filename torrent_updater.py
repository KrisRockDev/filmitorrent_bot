import json
import os
import requests  # Will remove if not directly used

# Settings
from settings import POSTED_MESSAGES_DB, CHANNEL_ID, base_dir_absolute

# Sender functions
from sendler.send_files import send_torrent_file

# Parser functions (assuming they will be modified as per Step 8)
from parser.parse_torrents import get_torrents
# For parse_info_file, I'll check where it's best to import from.
# It's in sendler.send_images.py but also used in send_to_telegram.py.
# For now, let's assume it might be moved to a more central utility or I'll import from send_images
from sendler.send_images import parse_info_file  # Tentative import

# Utility functions from send_to_telegram or to be duplicated/centralized
from send_to_telegram import torrent_file_info, load_posted_messages, save_posted_messages
from icecream import ic  # For logging/debugging
from dotenv import load_dotenv
load_dotenv()

# Замените на ваш токен бота и chat_id
BOT_TOKEN = os.getenv("TOKEN")

def check_movie_for_torrent_updates(movie_identifier, posted_movie_data, bot_token, channel_id):
    """
    Checks a specific movie for new torrent files and sends them to Telegram.
    """
    film_dir_path = os.path.join(base_dir_absolute, movie_identifier)
    info_file_path = os.path.join(film_dir_path, 'info.txt')
    newly_sent_this_run = []

    if not os.path.exists(info_file_path):
        ic(f"Error: info.txt not found for {movie_identifier} at {film_dir_path}")
        return newly_sent_this_run

    # d. Read info_file_path and extract movie_source_url
    try:
        movie_data_from_info_txt = parse_info_file(info_file_path)
        movie_source_url = movie_data_from_info_txt.get('url')  # Assuming 'url' is the key
        if not movie_source_url:
            ic(f"Error: Source URL not found in info.txt for {movie_identifier}")
            return newly_sent_this_run
    except Exception as e:
        ic(f"Error parsing info.txt for {movie_identifier}: {e}")
        return newly_sent_this_run

    ic(f"Checking for torrent updates for {movie_identifier} using URL: {movie_source_url}")

    # e. Call get_torrents (assuming modified version for update checks)
    # This assumes get_torrents (when is_update_check=True):
    # 1. Does NOT create a 'new' file.
    # 2. Downloads new torrents found on the page into film_dir_path if they don't already exist.
    # 3. Returns a list of filenames of ALL torrents currently available on the website for that movie URL.
    try:
        # For now, we'll simulate the output of the future get_torrents
        # In reality, this call would be:
        # current_torrents_on_page = get_torrents(url=movie_source_url, film_dir=film_dir_path, is_update_check=True)
        # The `film_dir` argument might be needed if `get_torrents` needs to know where to save.
        # For now, let's assume `get_torrents` handles saving to `film_dir_path` based on its internal logic or derived from `movie_identifier`.
        # The current `get_torrents` in `parser.parse_torrents` takes `url` and `s` (session) and `film_dir`.
        # We will need to pass `film_dir_path` to it.

        # Placeholder for session object if get_torrents requires it
        session = requests.Session()  # Or however the session is managed/created in other parts of the project

        current_torrents_on_page = get_torrents(url=movie_source_url, s=session, film_dir=film_dir_path,
                                                is_update_check=True)
        if current_torrents_on_page is None:  # get_torrents might return None on error
            ic(f"get_torrents returned None for {movie_identifier}, possibly an error fetching page or no torrents found.")
            return newly_sent_this_run

    except Exception as e:
        ic(f"Error calling get_torrents for {movie_identifier}: {e}")
        return newly_sent_this_run

    # f. Retrieve already_sent_torrents
    already_sent_torrents = posted_movie_data.get('sent_torrents', [])
    main_post_message_id = posted_movie_data.get('message_id')

    if not main_post_message_id:
        ic(f"Error: message_id not found in posted_movie_data for {movie_identifier}. Cannot send torrents as reply.")
        return newly_sent_this_run

    ic(f"Movie: {movie_identifier}, Already sent: {already_sent_torrents}, Current on page: {current_torrents_on_page}")

    # g. Identify and send new torrents
    for torrent_filename in current_torrents_on_page:
        if torrent_filename not in already_sent_torrents:
            ic(f"New torrent found for {movie_identifier}: {torrent_filename}")
            torrent_file_full_path = os.path.join(film_dir_path, torrent_filename)

            # Assuming get_torrents (with is_update_check=True) has already downloaded it to film_dir_path
            if not os.path.exists(torrent_file_full_path):
                ic(f"Error: New torrent {torrent_filename} not found at {torrent_file_full_path} after get_torrents call. Skipping.")
                # This indicates a potential mismatch in assumptions about get_torrents behavior.
                # For Step 7, we assume get_torrents downloads it.
                continue

            caption = torrent_file_info(torrent_filename)  # Generate caption

            ic(f"Sending new torrent: {torrent_filename} for {movie_identifier} as reply to {main_post_message_id}")
            send_success = send_torrent_file(
                bot_token=bot_token,
                chat_id=channel_id,
                file_name=torrent_file_full_path,
                caption=caption,
                reply_to_message_id=main_post_message_id
            )

            # send_torrent_file currently doesn't return status. Assuming it logs errors.
            # For robustness, it should return True/False. For now, assume success if no exception.
            # If send_success: # (when send_torrent_file is updated to return status)
            newly_sent_this_run.append(torrent_filename)
            # else:
            # ic(f"Failed to send torrent {torrent_filename} for {movie_identifier}")

    return newly_sent_this_run


def run_torrent_update_check():
    """
    Main function to iterate through posted movies and check for torrent updates.
    """
    bot_token = BOT_TOKEN
    channel_id = CHANNEL_ID

    if not bot_token:
        ic("Error: BOT_TOKEN not found. Cannot run torrent update check.")
        return
    if not channel_id:
        ic("Error: CHANNEL_ID not found. Cannot run torrent update check.")
        return

    ic("Starting torrent update check...")
    all_posted_data = load_posted_messages()

    if not all_posted_data:
        ic("No posted messages found in DB. Nothing to update.")
        return

    any_updates_made = False

    for movie_identifier, posted_data in all_posted_data.items():
        ic(f"Processing updates for movie: {movie_identifier}")
        if not isinstance(posted_data, dict):  # Basic check for data integrity
            ic(f"Warning: Invalid data format for {movie_identifier} in {POSTED_MESSAGES_DB}. Skipping.")
            continue

        newly_sent_torrents = check_movie_for_torrent_updates(
            movie_identifier,
            posted_data,
            bot_token,
            channel_id
        )

        if newly_sent_torrents:
            if 'sent_torrents' not in posted_data:
                posted_data['sent_torrents'] = []

            for nt in newly_sent_torrents:  # Ensure no duplicates if somehow one was sent but not recorded
                if nt not in posted_data['sent_torrents']:
                    posted_data['sent_torrents'].append(nt)
            any_updates_made = True
            ic(f"Updates found and sent for {movie_identifier}: {newly_sent_torrents}")
        else:
            ic(f"No new torrents found for {movie_identifier}.")

    if any_updates_made:
        ic("Saving updated posted messages DB...")
        save_posted_messages(all_posted_data)
        ic("Posted messages DB updated.")
    else:
        ic("No updates made across all movies.")

    ic("Torrent update check finished.")


if __name__ == '__main__':
    # This allows running the update check manually
    # In a production setup, this might be scheduled (e.g., cron job)
    run_torrent_update_check()
