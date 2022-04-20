"""This module provides the workout model-controller"""
"""Links Class to specific User Command"""
from pathlib import Path 
from typing import Any,Dict, List, NamedTuple
from workout import DB_READ_ERROR, ID_ERROR
import workout
from workout.database import DatabaseHandler

#Sub-class of NamedTuple class allowing for named fields 
class CurrentExercise(NamedTuple): 
    exercise: Dict[str, Any]
    error: int 

#Composition utilises DatabaseHandler to facilitate direct db communication
#Controller class
class Workouter: 
    def __init__(self, db_path: Path) -> None: 
        self._db_handler =  DatabaseHandler(db_path)
    
    def add(self, description: List[str], rank: int=2) -> CurrentExercise: 
        """Add a new exercise to the database"""
        description_text = " ".join(description)
        if not description_text.endswith("."):
            description_text += "."
        exercise = {
            "Description": description_text,
            "Rank": rank, 
            "Done": False
        }
        read = self._db_handler.read_exercises()
        if read.error == DB_READ_ERROR:
            return CurrentExercise(exercise, read.error)
        read.workout_list.append(exercise)
        write = self._db_handler.write_exercises(read.workout_list)
        return CurrentExercise(exercise, write.error)

    def get_workout_list(self) -> List[Dict[str, Any]]: 
        """Return the Current Exercise List."""
        read = self._db_handler.read_exercises()
        return read.workout_list
    
    def set_done(self, exercise_id: int) -> CurrentExercise:
        """Set an exercise as done."""
        read = self._db_handler.read_exercises()
        if read.error:
            return CurrentExercise({}, read.error)
        try:
            exercise = read.workout_list[exercise_id - 1]
        except IndexError:
            return CurrentExercise({}, ID_ERROR)
        exercise["Done"] = True
        write = self._db_handler.write_exercises(read.workout_list)
        return CurrentExercise(exercise, write.error)

    def remove(self, exercise_id: int) -> CurrentExercise:
        """Remove an exercise from the database using it's id or index."""
        read = self._db_handler.read_exercises()
        if read.error:
            return CurrentExercise({}, read.error)
        try:
            exercise = read.workout_list.pop(exercise_id - 1)
        except IndexError:
            return CurrentExercise({}, ID_ERROR)
        write = self._db_handler.write_exercises(read.workout_list)
        return CurrentExercise(exercise, write.error)

    def remove_all(self) -> CurrentExercise:
        """Remove all exercises from the database."""
        write = self._db_handler.write_exercises([])
        return CurrentExercise({}, write.error)
