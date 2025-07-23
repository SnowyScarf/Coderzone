import os
import uuid
from flask import render_template, request, redirect, url_for, flash, session, send_file, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from app import app, db, mail
from models import User, Project, Purchase, Review, Wishlist
from forms import LoginForm, RegisterForm, ProjectForm, SearchForm, ReviewForm
from datetime import datetime
from flask_wtf import FlaskForm


@app.route('/')
def index():
    search_form = SearchForm()
    featured_projects = Project.query.filter_by(is_featured=True).limit(6).all()
    if not featured_projects:
        featured_projects = Project.query.order_by(Project.created_at.desc()).limit(6).all()
    return render_template('index.html', featured_projects=featured_projects, search_form=search_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_seller=form.is_seller.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/browse')
def browse():
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    language = request.args.get('language', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search_query = request.args.get('q', '')

    query = Project.query

    if search_query:
        search_filter = or_(
            Project.title.ilike(f'%{search_query}%'),
            Project.description.ilike(f'%{search_query}%'),
            Project.tags.ilike(f'%{search_query}%'),
            Project.language.ilike(f'%{search_query}%')
        )
        query = query.filter(search_filter)

    if language:
        query = query.filter(Project.language == language)
    if category:
        query = query.filter(Project.category == category)
    if min_price is not None:
        query = query.filter(Project.price >= min_price)
    if max_price is not None:
        query = query.filter(Project.price <= max_price)

    projects = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=9, error_out=False
    )

    return render_template('browse.html', projects=projects, search_form=search_form,
                           language=language, category=category,
                           min_price=min_price, max_price=max_price, search_query=search_query)


@app.route('/project/<int:id>')
def product_detail(id):
    project = Project.query.get_or_404(id)
    project.views += 1
    db.session.commit()

    has_purchased = False
    can_review = False
    user_review = None
    is_wishlisted = False

    if current_user.is_authenticated:
        purchase = Purchase.query.filter_by(buyer_id=current_user.id, project_id=project.id, status='completed').first()
        has_purchased = purchase is not None

        if has_purchased:
            user_review = Review.query.filter_by(user_id=current_user.id, project_id=project.id).first()
            can_review = user_review is None

        wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, project_id=project.id).first()
        is_wishlisted = wishlist_item is not None

    related_projects = Project.query.filter(Project.category == project.category, Project.id != project.id).limit(
        4).all()
    reviews = Review.query.filter_by(project_id=project.id).order_by(Review.created_at.desc()).all()

    form = FlaskForm()
    review_form = ReviewForm()

    return render_template('product_detail.html', project=project,
                           has_purchased=has_purchased, related_projects=related_projects,
                           can_review=can_review, user_review=user_review,
                           is_wishlisted=is_wishlisted, reviews=reviews,
                           review_form=review_form, form=form)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.is_seller:
        flash('You need to be a seller to upload projects.', 'danger')
        return redirect(url_for('index'))

    form = ProjectForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)

        project = Project(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            language=form.language.data,
            category=form.category.data,
            tags=form.tags.data,
            filename=filename,
            file_path=file_path,
            seller_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Project uploaded successfully!', 'success')
        return redirect(url_for('seller_dashboard'))

    return render_template('upload.html', form=form)


@app.route('/seller/dashboard')
@login_required
def seller_dashboard():
    if not current_user.is_seller:
        flash('You need to be a seller to access this page.', 'danger')
        return redirect(url_for('index'))

    projects = Project.query.filter_by(seller_id=current_user.id).order_by(Project.created_at.desc()).all()

    total_earnings = current_user.get_earnings()
    total_views = sum(p.views for p in projects)
    total_downloads = sum(p.get_download_count() for p in projects)

    form = FlaskForm()

    return render_template('seller_dashboard.html',
                           projects=projects,
                           total_earnings=total_earnings,
                           total_views=total_views,
                           total_downloads=total_downloads,
                           form=form)


@app.route('/buyer/dashboard')
@login_required
def buyer_dashboard():
    purchases = Purchase.query.filter_by(buyer_id=current_user.id, status='completed').order_by(
        Purchase.completed_at.desc()).all()
    return render_template('buyer_dashboard.html', purchases=purchases)


@app.route('/buy/<int:project_id>', methods=['POST'])
@login_required
def buy_project(project_id):
    project = Project.query.get_or_404(project_id)

    if project.seller_id == current_user.id:
        flash('You cannot buy your own project.', 'danger')
        return redirect(url_for('product_detail', id=project_id))

    existing_purchase = Purchase.query.filter_by(buyer_id=current_user.id, project_id=project_id,
                                                 status='completed').first()

    if existing_purchase:
        flash('You have already purchased this project.', 'info')
        return redirect(url_for('product_detail', id=project_id))

    try:
        purchase = Purchase(
            buyer_id=current_user.id,
            project_id=project_id,
            amount=project.price,
            status='completed',
            completed_at=datetime.utcnow()
        )
        db.session.add(purchase)
        db.session.commit()

        try:
            send_payment_success_email(purchase)
            send_new_sale_email(purchase)
        except Exception as e:
            app.logger.error(f"Failed to send email after purchase: {str(e)}")

        flash('Purchase successful! You can now download your project.', 'success')
        return redirect(url_for('buyer_dashboard'))

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error during direct purchase: {str(e)}")
        flash('An error occurred during your purchase. Please try again.', 'danger')
        return redirect(url_for('product_detail', id=project_id))


@app.route('/download/<int:project_id>')
@login_required
def download_project(project_id):
    project = Project.query.get_or_404(project_id)

    purchase = Purchase.query.filter_by(buyer_id=current_user.id, project_id=project_id, status='completed').first()

    if not purchase and project.seller_id != current_user.id:
        flash('You have not purchased this project.', 'danger')
        return redirect(url_for('product_detail', id=project_id))

    if os.path.exists(project.file_path):
        return send_file(project.file_path, as_attachment=True, download_name=project.filename)
    else:
        flash('File not found on server.', 'danger')
        return redirect(url_for('buyer_dashboard'))


@app.route('/delete-project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)

    if project.seller_id != current_user.id:
        flash('You can only delete your own projects.')
        return redirect(url_for('seller_dashboard'))

    if os.path.exists(project.file_path):
        os.remove(project.file_path)

    Purchase.query.filter_by(project_id=project_id).delete()
    Review.query.filter_by(project_id=project_id).delete()
    Wishlist.query.filter_by(project_id=project_id).delete()

    db.session.delete(project)
    db.session.commit()

    flash('Project deleted successfully.', 'success')
    return redirect(url_for('seller_dashboard'))


def send_payment_success_email(purchase):
    if not app.config.get('MAIL_USERNAME'):
        return
    msg = Message(subject='Payment Successful - CodeMarket', recipients=[purchase.buyer.email],
                  body=f"Hi {purchase.buyer.username},\n\nYour payment for \"{purchase.project.title}\" has been processed successfully!\n\nAmount: ₹{purchase.amount:.2f}\nPurchase Date: {purchase.completed_at.strftime('%B %d, %Y')}\n\nYou can now download your project from your buyer dashboard.\n\nThank you for using CodeMarket!\n\nBest regards,\nThe CodeMarket Team")
    mail.send(msg)


def send_new_sale_email(purchase):
    if not app.config.get('MAIL_USERNAME'):
        return
    msg = Message(subject='New Sale - CodeMarket', recipients=[purchase.project.seller.email],
                  body=f"Hi {purchase.project.seller.username},\n\nGreat news! Someone just purchased your project \"{purchase.project.title}\".\n\nBuyer: {purchase.buyer.username}\nAmount: ₹{purchase.amount:.2f}\nSale Date: {purchase.completed_at.strftime('%B %d, %Y')}\n\nCheck your seller dashboard to see your updated earnings.\n\nCongratulations on your sale!\n\nBest regards,\nThe CodeMarket Team")
    mail.send(msg)


@app.route('/search')
def search():
    search_form = SearchForm()
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)

    if query:
        search_filter = or_(Project.title.ilike(f'%{query}%'), Project.description.ilike(f'%{query}%'),
                            Project.tags.ilike(f'%{query}%'), Project.language.ilike(f'%{query}%'))
        projects = Project.query.filter(search_filter).order_by(Project.created_at.desc()).paginate(page=page,
                                                                                                    per_page=9,
                                                                                                    error_out=False)
    else:
        projects = None

    return render_template('search_results.html', projects=projects, query=query, search_form=search_form)


@app.route('/project/<int:project_id>/review', methods=['POST'])
@login_required
def add_review(project_id):
    project = Project.query.get_or_404(project_id)
    purchase = Purchase.query.filter_by(buyer_id=current_user.id, project_id=project_id, status='completed').first()
    if not purchase:
        flash('You can only review projects you have purchased.')
        return redirect(url_for('product_detail', id=project_id))

    existing_review = Review.query.filter_by(user_id=current_user.id, project_id=project_id).first()
    if existing_review:
        flash('You have already reviewed this project.')
        return redirect(url_for('product_detail', id=project_id))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(user_id=current_user.id, project_id=project_id, rating=int(form.rating.data),
                        comment=form.comment.data)
        db.session.add(review)
        db.session.commit()
        flash('Review submitted successfully!', 'success')

    return redirect(url_for('product_detail', id=project_id))


@app.route('/wishlist/add/<int:project_id>')
@login_required
def add_to_wishlist(project_id):
    project = Project.query.get_or_404(project_id)
    existing = Wishlist.query.filter_by(user_id=current_user.id, project_id=project_id).first()
    if not existing:
        wishlist_item = Wishlist(user_id=current_user.id, project_id=project_id)
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Project added to your wishlist!', 'success')
    else:
        flash('Project is already in your wishlist.', 'info')
    return redirect(url_for('product_detail', id=project_id))


@app.route('/wishlist/remove/<int:project_id>')
@login_required
def remove_from_wishlist(project_id):
    wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, project_id=project_id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        flash('Project removed from your wishlist.', 'success')
    return redirect(request.referrer or url_for('product_detail', id=project_id))


@app.route('/wishlist')
@login_required
def wishlist():
    page = request.args.get('page', 1, type=int)
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).order_by(Wishlist.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)
    return render_template('wishlist.html', wishlist_items=wishlist_items)
