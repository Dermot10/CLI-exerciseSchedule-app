import json
from unittest import mock
import pytest
from typer.testing import CliRunner
from workout import (
    DB_READ_ERROR,
    SUCCESS,
    __app_name__, 
    __version__, 
    cli, 
    workout,
)

#sub-class of Clirunner, invoke returns result of running CLI app (exit codes, standard output)
runner = CliRunner()

def test_version(): 
    result = runner.invoke(cli.app, ['--version'])
    assert result.exit_code == 0 
    assert f"{__app_name__} v{__version__}\n" in result.stdout

@pytest.fixture
def mock_json_file(tmp_path): 
    exercise = [{"Description": "Bench Press", "Muscles": "Chest Shoulders Triceps", "Rank": 1 }]
    db_file = tmp_path / "workout.json"
    with db_file.open("w") as db: 
        json.dump(exercise, db, indent=4)
    return db_file


test_data1 = {
    "description": "Bench Press",
    "muscles": "Chest Shoulders Triceps",
    "rank": 1, 
    "exercise": {
        "Description": "Bench Press",
        "Muscles": "Chest Shoulders Triceps",
        "Rank": 1,
    }
}


@pytest.mark.parametrize(
    "description,  muscles, rank, expected",
    [
        pytest.param(
            test_data1["description"], 
            test_data1["muscles"],
            test_data1["rank"],
            (test_data1["exercise"], SUCCESS)
        )
    ],
)
def test_add(mock_json_file, description, muscles, rank, expected): 
    workouter = workout.Workouter(mock_json_file)
    assert workouter.add(description, muscles, rank) == expected
    read = workouter._db_handler.read_exercises()
    assert len(read.workout_list) == 2