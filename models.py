from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_seller = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship('Project', backref='seller', lazy=True)
    purchases = db.relationship('Purchase', backref='buyer', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_earnings(self):
        total = 0
        for project in self.projects:
            total += project.get_total_earnings()
        return total


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    language = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(500))
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)

    purchases = db.relationship('Purchase', backref='project', lazy=True)
    reviews = db.relationship('Review', backref='project', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='project', lazy=True)

    def get_total_earnings(self):
        return sum(purchase.amount for purchase in self.purchases if purchase.status == 'completed')

    def get_download_count(self):
        return len([p for p in self.purchases if p.status == 'completed'])

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []

    def get_average_rating(self):
        if not self.reviews:
            return 0
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 1)

    def get_review_count(self):
        return len(self.reviews)


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    razorpay_order_id = db.Column(db.String(100), nullable=True)
    razorpay_payment_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'project_id', name='unique_user_project_review'),)


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'project_id', name='unique_user_project_wishlist'),)
