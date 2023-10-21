from tools.sql import db


class Topics(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    # Attributs
    topic = db.Column(db.String(1000), nullable=True)
    history_size = db.Column(db.Integer, nullable=False)


class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    # Attributs
    topic = db.Column(db.String(300), nullable=False)
    state = db.Column(db.String(10000), nullable=True)
    date = db.Column(db.Date, nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
