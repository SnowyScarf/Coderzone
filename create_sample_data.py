from app import app, db
from models import User, Project, Purchase, Review, Wishlist # MODIFIED LINE
import random

# --- Sample Data ---

USERS = [
    {'username': 'codeNinja', 'email': 'ninja@example.com', 'is_seller': True},
    {'username': 'devQueen', 'email': 'queen@example.com', 'is_seller': True},
    {'username': 'pyMaster', 'email': 'master@example.com', 'is_seller': True},
    {'username': 'jsWizard', 'email': 'wizard@example.com', 'is_seller': True},
    {'username': 'dataDiva', 'email': 'diva@example.com', 'is_seller': True},
    {'username': 'logicLord', 'email': 'lord@example.com', 'is_seller': True},
    {'username': 'byteBabe', 'email': 'babe@example.com', 'is_seller': False},
    {'username': 'scriptKid', 'email': 'kid@example.com', 'is_seller': False},
    {'username': 'algoAce', 'email': 'ace@example.com', 'is_seller': False},
    {'username': 'syntaxSage', 'email': 'sage@example.com', 'is_seller': False},
    {'username': 'debugDemon', 'email': 'demon@example.com', 'is_seller': False},
    {'username': 'cloudCoder', 'email': 'cloud@example.com', 'is_seller': False},
    {'username': 'gitGuru', 'email': 'guru@example.com', 'is_seller': False},
    {'username': 'stackStar', 'email': 'star@example.com', 'is_seller': False},
    {'username': 'kernelKing', 'email': 'king@example.com', 'is_seller': False},
    {'username': 'loopLady', 'email': 'lady@example.com', 'is_seller': False},
    {'username': 'queryQueen', 'email': 'query@example.com', 'is_seller': False},
    {'username': 'apiArtist', 'email': 'artist@example.com', 'is_seller': False},
    {'username': 'frontEndFiend', 'email': 'fiend@example.com', 'is_seller': False},
    {'username': 'backEndBoss', 'email': 'boss@example.com', 'is_seller': False},
]

PROJECTS = [
    {'title': 'AI Chatbot for Customer Service', 'lang': 'python', 'cat': 'ai', 'price': 499.00},
    {'title': 'Mobile Fitness Tracker App', 'lang': 'javascript', 'cat': 'mobile', 'price': 799.00},
    {'title': 'Real-time Stock Market Dashboard', 'lang': 'python', 'cat': 'data', 'price': 1299.00},
    {'title': 'E-commerce Website Backend', 'lang': 'java', 'cat': 'api', 'price': 999.00},
    {'title': '2D Platformer Game Engine', 'lang': 'cpp', 'cat': 'game', 'price': 649.00},
    {'title': 'Social Media API Integration', 'lang': 'php', 'cat': 'api', 'price': 349.00},
    {'title': 'Data Visualization Library', 'lang': 'javascript', 'cat': 'data', 'price': 599.00},
    {'title': 'Inventory Management System', 'lang': 'csharp', 'cat': 'other', 'price': 899.00},
    {'title': 'Machine Learning Model Trainer', 'lang': 'python', 'cat': 'ml', 'price': 1499.00},
    {'title': 'Online Learning Platform', 'lang': 'javascript', 'cat': 'web', 'price': 1199.00},
    {'title': 'Task Automation Script Pack', 'lang': 'python', 'cat': 'other', 'price': 299.00},
    {'title': 'Secure User Authentication Module', 'lang': 'java', 'cat': 'api', 'price': 459.00},
    {'title': 'Node.js REST API Boilerplate', 'lang': 'javascript', 'cat': 'api', 'price': 349.00},
    {'title': 'Web Scraper for News Articles', 'lang': 'python', 'cat': 'data', 'price': 249.00},
    {'title': 'VR Mini-Game Collection', 'lang': 'csharp', 'cat': 'game', 'price': 899.00},
]

def create_sample_data():
    """Creates sample users and projects in the database."""
    with app.app_context():
        # First, delete existing data to avoid duplicates
        print("Deleting old data...")
        db.session.query(Purchase).delete()
        db.session.query(Review).delete()
        db.session.query(Wishlist).delete()
        db.session.query(Project).delete()
        db.session.query(User).delete()
        db.session.commit()
        print("Old data deleted.")

        # Create Users
        print("Creating new users...")
        user_objects = []
        for user_data in USERS:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                is_seller=user_data['is_seller']
            )
            user.set_password('password123') # All users have the same simple password
            db.session.add(user)
            user_objects.append(user)
        db.session.commit()
        print(f"{len(user_objects)} users created.")

        # Create Projects
        print("Creating new projects...")
        sellers = [u for u in user_objects if u.is_seller]
        for proj_data in PROJECTS:
            seller = random.choice(sellers)
            project = Project(
                title=proj_data['title'],
                description=f"This is a high-quality project for {proj_data['title']}. It is written in {proj_data['lang'].title()} and is perfect for the {proj_data['cat']} category. Includes full documentation and source files.",
                price=proj_data['price'],
                language=proj_data['lang'],
                category=proj_data['cat'],
                tags=f"{proj_data['lang']}, {proj_data['cat']}, app",
                filename=f"{proj_data['title'].replace(' ', '_').lower()}.zip",
                file_path=f"static/uploads/sample_project.zip", # Placeholder path
                seller_id=seller.id
            )
            db.session.add(project)
        db.session.commit()
        print(f"{len(PROJECTS)} projects created.")
        print("\nDatabase has been seeded successfully!")

if __name__ == '__main__':
    create_sample_data()
