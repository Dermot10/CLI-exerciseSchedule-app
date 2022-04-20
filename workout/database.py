"""This module provides the exerciseCLI database functionality."""

import configparser
import json
from pathlib import Path 
from typing import Any, Dict, List, NamedTuple
from workout import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS


DEFAULT_DB_FILE_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_workouts.json"
)

#List of dictionaries, with each Dict representing an individual item
#error field holds int return code
class DBResponse(NamedTuple): 
    workout_list: List[Dict[str, Any]]
    error: int

#Protected memeber for child class to utilise, database path
class DatabaseHandler: 
    def __init__(self, db_path: Path) -> None: 
        self._db_path = db_path

    #Read list by loading json file, and success code 
    def read_exercises(self) -> DBResponse: 
        try: 
            with self._db_path.open('r') as db: 
                try: 
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError: 
                    return DBResponse([], JSON_ERROR)
        except OSError: 
            return DBResponse([], DB_READ_ERROR)
        
    #Write to Json file in db 
    def write_exercises(self, workout_list: List[Dict[str,Any]]) -> DBResponse: 
        try:
            with self._db_path.open('w') as db: 
                json.dump(workout_list, db, indent=4)
            return DBResponse(workout_list, SUCCESS)
        except OSError: 
            return DBResponse(workout_list, DB_WRITE_ERROR)

#Parse through config file, return Path fields
def get_database_path(config_file: Path) -> Path: 
    """Return the current path to the workouts database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])

def init_database(db_path: Path) -> int: 
    """Initialise the database."""
    try:
        db_path.write_text("[]")
        return SUCCESS
    except OSError: 
        return DB_WRITE_ERROR
