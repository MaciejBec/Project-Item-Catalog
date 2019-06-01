from settings import db


class Category(db.Model):
    """ Class representing categories """

    __tablename__ = 'categories'
    id = db.Column(db.Integer, db.Sequence('category_id_seq'), primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    items = db.relationship('Item', backref='category')

    def __init__(self, name):
        self.name = name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'item': [x.serialize for x in self.items]
        }


class Item(db.Model):
    """ Class representing items """

    __tablename__ = 'items'
    id = db.Column(db.Integer, db.Sequence('item_id_seq'), primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    description = db.Column(db.String(100), nullable=False, unique=True)
    title = db.Column(db.String(40), nullable=False, unique=True)
    author = db.Column(db.String(80), nullable=False)

    def __init__(self, cat_id, description, title, author):
        self.cat_id = cat_id
        self.description = description
        self.title = title
        self.author = author

    @property
    def serialize(self):
        return {
            'id': self.id,
            'cat_id': self.cat_id,
            'description': self.description,
            'title': self.title
        }
