from functools import wraps
from flask import request, redirect, url_for, render_template, flash, abort, jsonify, session, g
from mono import app, db
from mono.models import User, Item


def login_required(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_view


@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(session['user_id'])


@app.route('/')
def show_items():
    items = Item.query.order_by(Item.updated_on.desc()).all()
    return render_template('show_items.html', items=items)


@app.route('/users/<int:user_id>/')
def user_detail(user_id):
    user = User.query.get(user_id)
    possession_items = Item.query.filter(Item.user_id == user_id, Item.status == 'possession').order_by(Item.updated_on.desc())
    considering_items = Item.query.filter(Item.user_id == user_id, Item.status == 'considering').order_by(Item.updated_on.desc())
    disposed_items = Item.query.filter(Item.user_id == user_id, Item.status == 'disposed').order_by(Item.updated_on.desc())
    return render_template('user_detail.html', user=user, possession_items=possession_items,
                           considering_items=considering_items, disposed_items=disposed_items)


@app.route('/items/add/', methods=['POST'])
def add_item():
    item = Item(
        name=request.form['name'],
        user_id=session['user_id'],
        description=request.form['description'],
        url=request.form['url'],
        category=request.form['category'],
        status=request.form['status']
    )
    db.session.add(item)
    db.session.commit()
    flash('New items was successufully posted')
    return redirect(url_for('item_detail', item_id=item.id))


@app.route('/items/new/')
def new_item():
    return render_template('new_item.html')


@app.route('/items/<int:item_id>/')
def item_detail(item_id):
    item = Item.query.get(item_id)
    return render_template('item_detail.html', item=item)


@app.route('/users/')
def user_list():
    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    if request.method == 'POST':
        user.name = request.form['name']
        user.password = request.form['password']
        db.session.commit()
        flash('User Updated!')
        items = Item.query.all()
        return redirect(url_for('user_detail', user_id=user_id, items=items))
    return render_template('user_edit.html', user=user)


@app.route('/users/create/', methods=['GET', 'POST'])
def user_create():
    if request.method == 'POST':
        user = User(name=request.form['name'],
                    password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('User created!Please login!')
        return redirect(url_for('login'))
    return render_template('user_edit.html')


# @app.route('/users/<int:user_id>/delete/', methods=['DELETE'])
# @login_required
# def user_delete(user_id):
#     user = User.query.get(user_id)
#     if user is None:
#         responce = jsonify({'status': 'Not Found'})
#         responce.status_code = 404
#         return responce
#     db.session.delete(user)
#     db.session.commit()
#     return jsonify({'status': 'OK'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user, authenticated = User.authenticate(db.session.query,
                                                request.form['name'], request.form['password'])
        if authenticated:
            session['user_id'] = user.id
            flash('You were logged in')
            items = Item.query.all()
            return redirect(url_for('user_detail', user_id=user.id, items=items))
        else:
            flash('Invalid email or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/items/<int:item_id>/edit/', methods=['GET', 'POST'])
@login_required
def item_edit(item_id):
    item = Item.query.get(item_id)
    if item is None:
        abort(404)
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.url = request.form['url']
        item.category = request.form['category']
        item.status = request.form['status']
        db.session.commit()
        return redirect(url_for('item_detail', item_id=item.id))
    return render_template('item_edit.html', item=item)
