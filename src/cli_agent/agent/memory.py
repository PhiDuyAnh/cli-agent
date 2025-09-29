import json
import os
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from pathlib import Path

import pixeltable as pxt
from pydantic import BaseModel
from loguru import logger

logger = logger.bind(name="Memory Management")


class MemoryRecord(BaseModel):
    message_id: str
    role: str
    content: str
    timestamp: datetime


class Memory:
    def __init__(self, memory_id: str):
        self._cache_dir = Path(".cache")
        self.cache_file_path = self._cache_dir / "conversation_history.json"

        # Check if the directory/table already exists
        if memory_id in pxt.list_dirs():
            self.directory = memory_id
        else:
            if memory_id.startswith("id_"):
                self.directory = memory_id
            # Use a valid directory name format for Pixeltable
            else:
                self.directory = f"id_{memory_id.replace('-', '')}"

            pxt.create_dir(self.directory, if_exists="replace_force")

            self._setup_table()

        self._memory_table = pxt.get_table(f"{self.directory}.memory")
        self._track_directory_in_json()

    def _setup_table(self):
        table_schema = {
            "message_id": pxt.String,
            "role": pxt.String,
            "content": pxt.String,
            "timestamp": pxt.Timestamp
        }
        pxt.create_table(
            f"{self.directory}.memory",
            schema=table_schema,
            if_exists="ignore",
        )

        logger.info("New memory table setup successfully")

    def _track_directory_in_json(self):
        """Use a JSON file to track saved Pixeltable directories."""
        self._cache_dir.mkdir(exist_ok=True)

        data = {}
        if self.cache_file_path.exists(): # Load the existing json file
            try:
                with open(self.cache_file_path, "r") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Could not read existing JSON file {self.cache_file_path}: {e}")
                data = {}
        
        # Intialize the list if key doesn't exist
        json_key = "memory_tables"
        if json_key not in data:
            data[json_key] = []
        
        # Append the Pixeltable directory if not present
        if self.directory not in data[json_key]:
            data[json_key].append(self.directory)

            # Write back to file
            try:
                with open(self.cache_file_path, "w") as f:
                    json.dump(data, f, indent=2)
                logger.info("Conversation history will be saved\n")
            except IOError:
                logger.error(f"Could not write to JSON file {self.cache_file_path}: {e}")
    
    def _remove_directory_from_json(self):
        """Remove the Pixeltable directory from cache."""
        if not self.cache_file_path.exists():
            logger.warning("No conversation history file to update")
            return

        try:
            with open(self.cache_file_path, "r") as f:
                data = json.load(f)
            
            json_key = "memory_tables"
            if json_key in data and self.directory in data[json_key]:
                data[json_key].remove(self.directory) # Remove the directory from list of directories

                with open(self.cache_file_path, "w") as f:
                    json.dump(data, f, indent=2) # Write back to file
                logger.info(f"Removed chat conversation from history")
            else:
                logger.warning("Conversation not found in history")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Could not update JSON file {self.cache_file_path}: {e}")
    
    def insert_memory(self, memory_record: MemoryRecord):
      # Disable logging messages to avoid it printing with agent responses
      with open(os.devnull, 'w') as devnull:
          with redirect_stdout(devnull), redirect_stderr(devnull):
            self._memory_table.insert([memory_record.model_dump()])

    def get_all_memory(self) -> list[MemoryRecord]:
        """Get all memory record of the table."""
        return [MemoryRecord(**record) for record in self._memory_table.collect()]
    
    def get_latest_memory(self, n: int) -> list[MemoryRecord]:
        """Get the n latest memory record."""
        return self.get_all_memory()[-n:]
    
    def reset_current_memory(self):
        logger.info("Resetting memory in current conversation")
        pxt.drop_dir(self.directory, if_not_exists="ignore", force=True)
        self._remove_directory_from_json()