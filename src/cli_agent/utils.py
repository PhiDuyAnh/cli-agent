import json
from datetime import datetime, timedelta
from typing import Optional

import pixeltable as pxt
from rich.console import Console

from cli_agent.agent.main_agent import Agent
from cli_agent.agent.memory import logger


def get_chat_history() -> Optional[tuple[list[str], list[str]]]:
    if not pxt.list_dirs():
        return [], []

    ids_with_timestamp = {} # Key: memory directory. Value: Latest message's timestamp
    
    for dir in pxt.list_dirs():
        memory_table = pxt.get_table(f"{dir}.memory")
        if memory_table.collect():
            latest_msg_timestamp = memory_table.collect()[-1]["timestamp"]
            ids_with_timestamp[dir] = latest_msg_timestamp
        
        # Handle newly created table with no messages
        else:
            creation_time = memory_table.history()["created_at"][0]
            local_timestamp = creation_time.to_pydatetime().astimezone()
            ids_with_timestamp[dir] = local_timestamp

    sorted_ids = list(reversed(sorted(ids_with_timestamp.keys(), key=ids_with_timestamp.get)))

    latest_user_msgs = [] # Only display the latest user message and last modified time
    for dir in sorted_ids:
        memory_table = pxt.get_table(f"{dir}.memory")

        if memory_table.collect():
            latest_timestamp = memory_table.collect()[-1]["timestamp"]
            for record in reversed(memory_table.collect()):
                if record["role"] == "user":
                    time_string = format_elapsed_time(
                        elapsed_timedelta=(datetime.now().astimezone() - latest_timestamp)
                    )
                    latest_user_msgs.append(f"{dir} - Modified {time_string} - {record["content"]}")
                    break

        # Handle newly created table with no messages
        else:
            creation_time = memory_table.history()["created_at"][0]
            local_timestamp = creation_time.to_pydatetime().astimezone()
            time_string = format_elapsed_time(
                elapsed_timedelta=datetime.now().astimezone() - local_timestamp
            )
            latest_user_msgs.append(f"{dir} - Modified {time_string} - No prompt")

    return latest_user_msgs, sorted_ids


def print_past_conversation(memory_id: str, console: Console):
    """Print user prompts and final agent responses of the resumed conversation."""
    memory_table = pxt.get_table(f"{memory_id}.memory")
    for record in memory_table.collect():
        if record["role"] == "user":
            console.print(f"[bold cornflower_blue]You[/bold cornflower_blue]: {record["content"]}")
        elif record["role"] == "assistant":
            console.print(f"\n[bold dark_red]Assistant[/bold dark_red]: {record["content"]}\n")


def delete_conversation(agent: Agent, memory_id: str):
    """Delete a specific conversation."""
    pxt.drop_dir(memory_id, force=True)

    # Remove from .cache file
    cache_dir = agent.memory.cache_file_path
    if not cache_dir.exists():
        return

    try:
        with open(cache_dir, "r") as f:
            data = json.load(f)
        
        json_key = "memory_tables"
        if json_key in data and memory_id in data[json_key]:
            data[json_key].remove(memory_id) # Remove the directory from list of directories

            with open(cache_dir, "w") as f:
                json.dump(data, f, indent=2) # Write back to file
        else:
            return
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Could not update JSON file {cache_dir}: {e}")


def format_elapsed_time(elapsed_timedelta: timedelta) -> str:
    """
    Format elapsed time between current time and last time the conversation was modified into a human-readable string.
    
    Args:
        elapsed_timedelta (datetime.timedelta): The time duration to format
    
    Returns:
        str: Human-readable string showing elapsed days, hours, minutes or seconds depending on the time.
    """
    total_seconds = elapsed_timedelta.total_seconds()

    if total_seconds >= 86400:
        return f"{total_seconds / 86400:.0f} day(s) ago"
    elif total_seconds >= 3600:
        return f"{total_seconds / 3600:.0f}h ago"
    elif total_seconds >= 60:
        return f"{total_seconds / 60:.0f}m ago"
    else:
        return f"{total_seconds:.0f}s ago"