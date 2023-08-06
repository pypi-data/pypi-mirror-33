from .db import db


class User(db.Model):
    email = db.Column(db.String(255), primary_key=True)
    type = db.Column(
        db.String(80),
        db.ForeignKey('user_type.name'),
        nullable=False,
        default='Employee',
    )
    Type = db.relationship('UserType', backref=db.backref('users', lazy=True))

    def __str__(self):
        return self.name


class UserType(db.Model):
    name = db.Column(db.String(80), primary_key=True)

    def __str__(self):
        return self.name


class Map(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    marker = db.Column(db.JSON, nullable=False)
    zone = db.Column(db.JSON, nullable=False)


class Category(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    display_name = db.Column(db.String(80))

    def __str__(self):
        return self.name


properties = db.Table(
    'properties',
    db.Column('product', db.String(80), db.ForeignKey('product.name'), primary_key=True),
    db.Column('property', db.String(80), db.ForeignKey('property.name'), primary_key=True),
)


options = db.Table(
    'options',
    db.Column('product', db.String(80), db.ForeignKey('product.name'), primary_key=True),
    db.Column('option', db.String(80), db.ForeignKey('option.name'), primary_key=True),
)


class Product(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    display_name = db.Column(db.String(80))
    category = db.Column(db.String(80), db.ForeignKey('category.name'), nullable=False)
    Category = db.relationship('Category', backref=db.backref('products', lazy=True))
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    properties = db.relationship(
        'Property',
        secondary=properties,
        lazy='subquery',
        backref=db.backref('products', lazy=True),
    )
    options = db.relationship(
        'Option',
        secondary=options,
        lazy='subquery',
        backref=db.backref('products', lazy=True),
    )

    def __str__(self):
        return self.name


class Property(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    display_name = db.Column(db.String(80))

    def __str__(self):
        return self.name


choices = db.Table(
    'choices',
    db.Column('option', db.String(80), db.ForeignKey('option.name'), primary_key=True),
    db.Column('choice', db.String(80), db.ForeignKey('choice.name'), primary_key=True),
)


class Option(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    display_name = db.Column(db.String(80))
    choices = db.relationship(
        'Choice',
        secondary=choices,
        lazy='subquery',
        backref=db.backref('options', lazy=True),
    )

    def __str__(self):
        return self.name


class Choice(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    display_name = db.Column(db.String(80))

    def __str__(self):
        return self.name
