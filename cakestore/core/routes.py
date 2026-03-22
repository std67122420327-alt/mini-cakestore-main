from flask import Blueprint, render_template, request, abort
from cakestore.extensions import db
from cakestore.models import Cake, Category

core_bp = Blueprint('core', __name__, template_folder='templates')

@core_bp.route('/')
def index():
    page = request.args.get('page', type=int)
    cakes = db.paginate(db.select(Cake), per_page=4, page=page)
    return render_template('core/index.html', title='Home Page', page=page, cakes=cakes)

@core_bp.route('/<int:id>/details')
def details(id):
    cake = db.session.get(Cake, id)
    if not cake:
        abort(404)
    return render_template('core/cake_detail.html', title='Details Page', cake=cake)