"""This module provides the exerciseCLI."""
"""User Input commands, Option providing acceptable paramaters """


from pathlib import Path
from typing import List, Optional
import typer
from workout import ERRORS, __app_name__, __version__, config, database, workout

app = typer.Typer()

@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH), 
        "--db-path", 
        "-db", 
        prompt="workout database location?"
    )
)-> None: 
    """Initialise the database"""
    app_init_error = config.init_app(db_path)
    if app_init_error: 
        typer.secho(
            f"Creating config file failed with '{ERRORS [app_init_error]}'",
            fg=typer.colors.RED, 
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error: 
        typer.secho(
            f"Creating the database failed with '{ERRORS[app_init_error]}'", 
            fg=typer.colors.RED, 
        )
        raise typer.Exit(1)
    else: 
        typer.secho(f"The workout database is  {db_path}", fg=typer.colors.GREEN)

def get_workouter() -> workout.Workouter: 
    if config.CONFIG_FILE_PATH.exists(): 
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else: 
        typer.secho(
            "Config file not found. Please, run 'workout init'", 
            fg=typer.colors.RED, 
        )
        raise typer.Exit(1)
    if db_path.exists(): 
        return workout.Workouter(db_path)
    else: 
        typer.secho(
            "Database not found. Please, run 'workout init'", 
            fg=typer.colors.RED
        )
        raise typer.Exit(1)
    
@app.command()
def add(
    description: List[str] = typer.Argument(...), 
    rank: int = typer.Option(2, "--rank", "-r", min=1, max=3),
) -> None: 
    """Add a new exercise with a Description."""
    workouter = get_workouter()
    exercise, error = workouter.add(description, rank)
    if error: 
        typer.secho(
            f"Adding exercise failed with '{ERRORS[error]}'", 
            fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else: 
        typer.secho(
            f"""exercise: "{exercise['Description']}" was added """
            f"""it is a rank: "{rank}" exercise""", 
            fg=typer.colors.GREEN
        )

@app.command(name="list")
def list_all() -> None: 
    """List all of the Exercises."""
    workouter = get_workouter()
    workout_list = workouter.get_workout_list()
    if len(workout_list) == 0: 
        typer.secho(
            "There are no exercises in the workout list yet", 
            fg=typer.colors.RED
        )
        raise typer.Exit(1)
    typer.secho("\n Exercise List:\n", fg=typer.colors.BLUE, bold=True)
    columns = (
        "ID.   ", 
        "| Rank   ", 
        "| Done   ", 
        "| Description   ",
    )
    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers), fg=typer.colors.BLUE)
    for id, workouts in enumerate(workout_list, 1):
        desc, rank, done = workouts.values()
        typer.secho(
            f"{id}{(len(columns[0]) - len(str(id))) * ' '}"
            f"| ({rank}){(len(columns[1]) - len(str(rank)) - 4) * ' '}"
             f"| {done}{(len(columns[2]) - len(str(done)) - 2) * ' '}"
            f"| {desc}",
            fg=typer.colors.BLUE,
        )
    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)

@app.command(name="complete")
def set_done(exercise_id: int = typer.Argument(...)) -> None:
    """Complete an exercise by setting it as done using its EXERCISE_ID."""
    workouter = get_workouter()
    exercise, error = workouter.set_done(exercise_id)
    if error:
        typer.secho(
            f'Completing exercise # "{exercise_id}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
            ) 
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""to-do # {exercise_id} "{exercise['Description']}" completed!""", 
            fg=typer.colors.GREEN,
            )


@app.command()
def remove(
    exercise_id: int = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove an exercise using its exercise_ID."""
    workouter = get_workouter()

    def _remove():
        exercise, error = workouter.remove(exercise_id)
        if error:
            typer.secho(
                f"Removing exercise # {exercise_id} failed with '{ERRORS[error]}'",
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho(
                f"""exercise # {exercise_id}: '{exercise["Description"]}' was removed""",
                fg=typer.colors.GREEN,
            )
    if force:
        _remove()
    else:
        workout_list = workouter.get_workout_list()
        try:
            exercise = workout_list[exercise_id- 1]
        except IndexError:
            typer.secho("Invalid EXERCISE ID", fg=typer.colors.RED)
            raise typer.Exit(1)
        delete = typer.confirm(
            f"Delete exercise # {exercise_id}: {exercise['Description']}?"
        )
        if delete:
            _remove()
        else:
            typer.secho("Operation cancelled")


@app.command(name="clear")
def remove_all(
    force: bool = typer.Option(
        ...,
        prompt="Delete all exercises?",
        help="Force deletion without confirmation.",
    )
) -> None:
    """Remove all exercises."""
    workouter = get_workouter()
    if force:
        error = workouter.remove_all().error
        if error:
            typer.secho(
                f"Removing exercises failed with '{ERRORS[error]}' ",
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho("All exercises were removed", fg=typer.colors.GREEN)
    else:
        typer.echo("Operation cancelled")

def _version_callback(value: bool) -> None: 
    if value: 
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        "-v", 
        help="Show the application's version and exit.",
        callback=_version_callback, 
        is_eager=True, 
    )
) -> None: 
    return 


