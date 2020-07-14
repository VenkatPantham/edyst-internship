from flask import Flask,request, json, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_simple import JWTManager,create_jwt,get_jwt_identity,jwt_required
from datetime import datetime
from sqlalchemy import and_ ,desc
import os
import re 

# Initializing App
app = Flask(__name__)

# for validating an Admin 
regex = '^[a-z0-9]+[\._]?[a-z0-9]+@edyst.com$'

basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+ os.path.join(
    basedir, "db.sqlite"
)

app.config["SQLALCHEMY_TRACK_MODIFICAIONS"] = False
app.config['JWT_SECRET_KEY'] = 'edyst-secret'
app.config['JSON_SORT_KEYS'] = False    

# Initializing Database
db = SQLAlchemy(app)
jwt=JWTManager(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)

    def __init__(self,email,password):
        self.email=email
        self.password=password

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
    restaurantId=db.Column(db.Integer,nullable=False)
    reviewerId=db.Column(db.Integer,nullable=False)
    review=db.Column(db.String,nullable=False)
    createdAt=db.Column(db.DateTime)
    updatedAt=db.Column(db.DateTime)

    def __init__(self,restaurantId,reviewerId,review,createdAt,updatedAt):
        self.restaurantId=restaurantId
        self.reviewerId=reviewerId
        self.review=review
        self.createdAt=createdAt
        self.updatedAt=updatedAt


@app.route('/api/v1/auth/signup',methods=['POST'])
def signup():
    registration=request.get_json()
    email=registration['user']['email']
    password=registration['user']['password']
    db.session.add(User(email,password))
    db.session.commit()
    data=User.query.filter(User.email==email).first()
    user={
        "user":{
            "email":data.email,
            "password":data.password,
        }
    }
    return jsonify(user),200

@app.route('/api/v1/auth/signin',methods=['POST'])
def login():  
    login=request.get_json()
    email=login['user']['email']
    password=login['user']['password']
    if(User.query.filter(User.email==email).first()):
        data=User.query.filter(User.email==email).first()
        if(User.query.filter(data.password==password).first()):
            token=create_jwt(identity=email)
            userdata={
                "user":{
                    "email":data.email,
                    "token":token
                }
            }
            return jsonify(userdata)
        else:
            return('Wrong Credentials'),403
    else:
        return('No Account is associated with this Email ID'),404

@app.route('/api/v1/restaurant',methods=['POST'])
@jwt_required
def add_restaurant():
    user=get_jwt_identity()
    if(re.search(regex,user)):
        data=request.get_json()
        name=data['restaurant']['name']
        description=data['restaurant']['description']
        createdAt=datetime.now()
        updatedAt=datetime.now()
        db.session.add(Restaurant(name,description,createdAt,updatedAt))
        db.session.commit()
        data=Restaurant.query.filter(Restaurant.name==name).first()
        restaurant={
            "restaurant":{
                "id":data.id,
                "name":data.name,
                "description":data.description,
                "createdAt":data.createdAt,
                "updatedAt":data.updatedAt
            }
        }
        return jsonify(restaurant),200
    else:
        return('Only Admin can Add the Restaurant'),403

@app.route('/api/v1/restaurant/<id>',methods=['PATCH','DELETE'])
@jwt_required
def edit_restaurant(id):
    if(Restaurant.query.filter(Restaurant.id==id).count()>0):
        user=get_jwt_identity()
        if(re.search(regex,user)):
            if request.method=='PATCH':
                restaurant=Restaurant.query.filter(Restaurant.id==id).first()
                data=request.json['restaurant']
                if 'name' in data:
                    restaurant.name=data['name']
                if 'description' in data:
                    restaurant.description=data['description']
                restaurant.updatedAt=datetime.now()
                db.session.commit()
                restaurant=Restaurant.query.filter(Restaurant.id==id).first()
                restaurantdata={
                    'restaurant':{
                        'id':restaurant.id,
                        'name':restaurant.name,
                        'description':restaurant.description,
                        'createdAt':restaurant.createdAt,
                        'updatedAt':restaurant.updatedAt,
                    }
                }
                return jsonify(restaurantdata),201
            elif request.method=='DELETE':
                restaurant=Restaurant.query.filter(Restaurant.id==id).first()
                db.session.delete(restaurant)
                db.session.commit()
                return jsonify(),204
        else:
            return('Only Admin can Edit/Delete the Restaurant'),403
    else:
        return('No Restaurant found with that ID'),404

@app.route('/api/v1/restaurant',methods=['GET'])
def get_restaurants():
    restaurants=Restaurant.query.all()
    restaurantdata={
        'restaurants':[
            {
                'id':restaurant.id,
                'name':restaurant.name,
                'description':restaurant.description,
                'createdAt':restaurant.createdAt,
                'updatedAt':restaurant.updatedAt
            }
            for restaurant in restaurants
        ]
    }
    return jsonify(restaurantdata),200

@app.route('/api/v1/restaurant/<id>',methods=['GET'])
def get_restaurant(id):
    if(Restaurant.query.filter(Restaurant.id==id).count()>0):
        restaurant=Restaurant.query.filter(Restaurant.id==id).first()
        reviews=Review.query.filter(Review.restaurantId==id).all()
        restaurantdata={
            'restaurant':{
                'id':restaurant.id,
                'name':restaurant.name,
                'description':restaurant.description,
                'createdAt':restaurant.createdAt,
                'updatedAt':restaurant.updatedAt,
                'reviews':[
                    {
                        'id':review.id,
                        'restaurantId':review.restaurantId,
                        'reviewerId':review.reviewerId,
                        'review':review.review,
                        'createdAt':review.createdAt,
                        'updatedAt':review.updatedAt
                    }
                for review in reviews
                ]
            }
        }
        return jsonify(restaurantdata),200
    else:
        return('No Restaurant found with that ID'),404

@app.route('/api/v1/restaurant/<id>/review',methods=['POST'])
@jwt_required
def add_review(id):
    if(Restaurant.query.filter(Restaurant.id==id).count()>0):
        email=get_jwt_identity()
        user=User.query.filter(User.email==email).first()
        data=request.get_json()
        restaurantId=int(id)
        reviewerId=int(user.id)
        review=data['review']['review']
        createdAt=datetime.now()
        updatedAt=datetime.now()
        db.session.add(Review(restaurantId,reviewerId,review,createdAt,updatedAt))
        db.session.commit()
        data=Review.query.filter(Review.restaurantId==id).order_by(desc(Review.updatedAt)).first()
        reviewdata={
            "review":{
                "id":data.id,
                "restaurantId":data.restaurantId,
                "reviewerId":data.reviewerId,
                "review":data.review,
                "createdAt":data.createdAt,
                "updatedAt":data.updatedAt
            }
        }
        return jsonify(reviewdata),200
    else:
        return('No Restaurant found with that ID'),404

@app.route('/api/v1/restaurant/<resId>/review/<revId>',methods=['PATCH','DELETE'])
@jwt_required
def edit_review(resId,revId):
    if(Restaurant.query.filter(Restaurant.id==resId).count()>0):
        if(Review.query.filter(Review.id==revId).count()>0):
            email=get_jwt_identity()
            user=User.query.filter(User.email==email).first()
            review=Review.query.filter(Review.id==revId).first()
            if(user.id==review.reviewerId):
                if request.method=='PATCH':
                    data=request.get_json()
                    review.review=data['review']['review']
                    review.updatedAt=datetime.now()
                    db.session.commit()
                    data=Review.query.filter(Review.id==revId).first()
                    reviewdata={
                        "review":{
                            "id":data.id,
                            "restaurantId":data.restaurantId,
                            "reviewerId":data.reviewerId,
                            "review":data.review,
                            "createdAt":data.createdAt,
                            "updatedAt":data.updatedAt
                        }
                    }
                    return jsonify(reviewdata),201
                elif request.method=='DELETE':
                    data=Review.query.filter(Review.id==revId).first()
                    db.session.delete(data)
                    db.session.commit()
                    return jsonify(),204
            else:
                return('You cannot edit this Review'),403
        else:
            return('No Review found with that ID'),404
    else:
        return('No Restaurant found with that ID'),404

@app.route('/api/v1/review',methods=['GET'])
def get_reviews():
    reviews=Review.query.all()
    reviewdata={
        'reviews':[
            {
                'id':review.id,
                'restaurantId':review.restaurantId,
                'reviewerId':review.reviewerId,
                'review':review.review,
                'createdAt':review.createdAt,
                'updatedAt':review.updatedAt
            }
            for review in reviews
        ]
    }
    return jsonify(reviewdata),200

@app.route('/api/v1/review/<id>',methods=['GET'])
def get_review(id):
    if(Review.query.filter(Review.id==id).count()>0):
        review=Review.query.filter(Review.id==id).first()
        reviewdata={
            'review':{
                'id':review.id,
                'restaurantId':review.restaurantId,
                'reviewerId':review.reviewerId,
                'review':review.review,
                'createdAt':review.createdAt,
                'updatedAt':review.updatedAt
            }
        }
        return jsonify(reviewdata),200
    else:
        return('No Review found with that ID'),404

if __name__ == "__main__":
    db.create_all()
app.run(host="localhost", port=8000,debug=True)