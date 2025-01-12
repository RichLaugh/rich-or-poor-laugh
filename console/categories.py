import click
from database import SessionLocal
from crud.category import insert_categories

@click.command()
def add_categories():
    if add_categories:
        db = SessionLocal()
        insert_categories(db)
        print("Categories have been added to the database.")
    else:
        print("No action specified.")