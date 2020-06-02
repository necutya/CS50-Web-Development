import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def csv_reader(csv_obj):
    reader = csv.reader(csv_obj)
    return reader

def add_to_db(csv_obj):
    engine = create_engine(os.environ.get("DATABASE_URL"))
    db = scoped_session(sessionmaker(bind=engine))
    for row in  list(csv_reader(csv_obj))[1:]:
        isbn, title, author, year = row
        db.execute(f"INSERT INTO \"books\" (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()

if __name__ == '__main__':
    csv_path = "books.csv"
    with open(csv_path, 'r') as file:
        add_to_db(file)
