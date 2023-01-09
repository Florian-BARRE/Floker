if __name__ == "__main__":
    from tools.sql import app, db
    from table import Topics, History
    with app.app_context():
        db.drop_all()
        db.create_all()