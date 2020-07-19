from app import db, bcrypt

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password_hash=db.Column(db.String,nullable=False)

    def __init__(self,email):
        self.email=email

    def set_password(self,password):
        self.password_hash=bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.check_password_hash(self.password_hash,password)

class Restaurant(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,unique=True,nullable=False)
    description=db.Column(db.String,nullable=False)    
    createdAt=db.Column(db.DateTime)
    updatedAt=db.Column(db.DateTime)

    def __init__(self,name,description,createdAt,updatedAt):
        self.name=name
        self.description=description
        self.createdAt=createdAt
        self.updatedAt=updatedAt

class Review(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    restaurantId=db.Column(db.Integer,db.ForeignKey('restaurant.id'),nullable=False)
    reviewerId=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    review=db.Column(db.String,nullable=False)
    createdAt=db.Column(db.DateTime)
    updatedAt=db.Column(db.DateTime)
    user=db.relationship('User',backref=db.backref('user',uselist=False,cascade="all,delete"))
    restaurant=db.relationship('Restaurant',backref=db.backref('restaurant',uselist=False,cascade="all,delete"))

    def __init__(self,restaurantId,reviewerId,review,createdAt,updatedAt):
        self.restaurantId=restaurantId
        self.reviewerId=reviewerId
        self.review=review
        self.createdAt=createdAt
        self.updatedAt=updatedAt