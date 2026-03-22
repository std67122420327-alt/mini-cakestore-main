from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from cakeshop.extensions import db
from cakeshop.models import Cake, User, Category
from flask_login import current_user, login_required

cake_bp = Blueprint('cake', __name__, template_folder='templates')

@cake_bp.route('/')
@login_required
def index():
    query = db.select(Cake).where(Cake.user == current_user)
    cakes = db.session.scalars(query).all()
    return render_template('cakes/index.html', title='My Cakes', cakes=cakes)

@cake_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_cake():
    
    cake_categories = db.session.scalars(db.select(Category)).all()
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        img_url = request.form.get('img_url')
        category_ids = request.form.getlist('cake_categories')
        user_id = current_user.id

        cats = []
        for cid in category_ids:
            cat = db.session.get(Category, int(cid))
            if cat:
                cats.append(cat)

        cake = Cake(
            name=name,
            price=price,
            description=description,
            img_url=img_url,
            user_id=user_id,
            categories=cats
        )
        db.session.add(cake)
        db.session.commit()
        flash(f'เพิ่มเมนูเค้ก {name} เรียบร้อยแล้ว 🍰', 'success')
        return redirect(url_for('cake.index'))
    
    return render_template('cakes/new_cake.html', title='เพิ่มเมนูเค้ก', cake_categories=cake_categories)

@cake_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_cake(id):
    cake = db.session.get(Cake, id)
    if not cake:
        abort(404)
    if cake.user_id != current_user.id:
        abort(403)
    
    cake_categories = db.session.scalars(db.select(Category)).all()
    if request.method == 'POST':
        cake.name = request.form.get('name')
        cake.price = request.form.get('price')
        cake.description = request.form.get('description')
        cake.img_url = request.form.get('img_url')
        category_ids = request.form.getlist('cake_categories')

        cats = []
        for cid in category_ids:
            cat = db.session.get(Category, int(cid))
            if cat:
                cats.append(cat)
        cake.categories = cats

        db.session.commit()
        flash(f'แก้ไขเมนูเค้ก {cake.name} เรียบร้อยแล้ว ✨', 'success')
        return redirect(url_for('cake.index'))
    
    return render_template('cakes/edit_cake.html', title='แก้ไขเมนูเค้ก', cake=cake, cake_categories=cake_categories)

@cake_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_cake(id):
    cake = db.session.get(Cake, id)
    if not cake:
        abort(404)
    if cake.user_id != current_user.id:
        abort(403)
    
    cake_name = cake.name
    db.session.delete(cake)
    db.session.commit()
    flash(f'ลบเมนูเค้ก {cake_name} เรียบร้อยแล้ว', 'success')
    return redirect(url_for('cake.index'))

@cake_bp.route('/search')
def search():
    q = request.args.get('q', '')
    cakes = []
    if q:
        query = db.select(Cake).where(Cake.name.ilike(f'%{q}%'))
        cakes = db.session.scalars(query).all()
    return render_template('cakes/search_results.html', title='ผลการค้นหาเค้ก', cakes=cakes, q=q)

@cake_bp.route('/search-live')
def search_live():
    q = request.args.get('q', '')
    cakes = []
    if q and len(q) >= 1:
        query = db.select(Cake).where(Cake.name.ilike(f'%{q}%')).limit(5)
        cakes = db.session.scalars(query).all()
    return render_template('cakes/search_dropdown.html', cakes=cakes, q=q)