from flask import redirect, render_template, flash, request, jsonify, url_for
from forms import UserForm
from database import User, Permission, user_schema, users_schema, permissions_schema
from database import app, db


@app.route('/')
def home():
    return redirect('users')


# now the users
@app.route('/users', methods=['GET', 'POST'])
def users():
    users_to_show = User.query.all()
    return render_template('users.html', users=users_to_show)


@app.route('/add/user', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if request.method == 'POST':
        new_user = User(name=request.form.get("name"), surname=request.form.get("surname"),
                        email=request.form.get("email"))

        permissions = request.form.getlist('permissions')
        if permissions.__contains__('Write' or 'Delete'):
            new_user.role = 'Editor'
        else:
            new_user.role = 'Viewer'

        db.session.add(new_user)
        db.session.commit()
        for p in permissions:
            new_permission = Permission(description=p, user_id=new_user.id)
            db.session.add(new_permission)
        db.session.commit()
        flash("Form submitted successfully")
        return redirect('/users')
    return render_template('addUser.html', form=form)


@app.route('/update/user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    user_to_update = User.query.get_or_404(user_id)

    # Get all descriptions of the permissions -> I need this for the template
    list_perm = []
    for p in user_to_update.permissions:
        list_perm.append(p.description)

    # Update the User information
    form = UserForm()
    if request.method == "POST":
        user_to_update.name = request.form['name']
        user_to_update.surname = request.form['surname']
        user_to_update.email = request.form['email']
        per = request.form.getlist('permissions')

        # Update the role of the user
        if per.__contains__('Write'):
            user_to_update.role = 'Editor'
        elif per.__contains__('Delete'):
            user_to_update.role = 'Editor'
        else:
            user_to_update.role = 'Viewer'

        # Delete the old permissions
        permissions_old = Permission.query.filter_by(user_id=user_to_update.id)
        for p in permissions_old:
            db.session.delete(p)
        db.session.commit()

        # Add new permissions
        for p in per:
            new_permission = Permission(description=p, user_id=user_to_update.id)
            db.session.add(new_permission)

        db.session.commit()
        flash("User updated successfully!")
        return redirect('/users')
    return render_template('updateUser.html', form=form, user_to_update=user_to_update, list_perm=list_perm)


@app.route('/delete/user/<int:user_id>')
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("User deleted successfully!")
    return redirect('/users')


# FLASK API FOR USERS
# Get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    output = users_schema.dump(all_users)
    return jsonify({'users': output})


# Get one user
@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user_to_show = User.query.get_or_404(user_id)
    output = user_schema.dump(user_to_show)
    return jsonify({'user': output})


# Add new user
@app.route('/api/add/user', methods=['POST'])
def api_add_user():
    req = request.get_json()
    user_name = req['name']
    user_surname = req['surname']
    user_email = req['email']
    user_permissions = req['permissions']

    new_user = User(name=user_name, surname=user_surname, email=user_email)
    if user_permissions.__contains__('Write'):
        new_user.role = 'Editor'
    elif user_permissions.__contains__('Delete'):
        new_user.role = 'Editor'
    else:
        new_user.role = 'Viewer'

    db.session.add(new_user)
    db.session.commit()

    for p in user_permissions:
        new_permission = Permission(description=p, user_id=new_user.id)
        db.session.add(new_permission)

    db.session.commit()
    return redirect(url_for("get_users"))


# Update current user
@app.route('/api/update/user/<int:user_id>', methods=['PATCH'])
def api_update_user(user_id):
    req = request.get_json()
    user_to_update = User.query.get_or_404(user_id)
    user_to_update.name = req['name']
    user_to_update.surname = req['surname']
    user_to_update.email = req['email']
    permissions = req['permissions']

    # Updating the user.role according to the new permissions
    if permissions.__contains__('Write'):
        user_to_update.role = 'Editor'
    elif permissions.__contains__('Delete'):
        user_to_update.role = 'Editor'
    else:
        user_to_update.role = 'Viewer'

    db.session.add(user_to_update)
    db.session.commit()

    # Deleting the old permissions
    permissions_old = Permission.query.filter_by(user_id=user_to_update.id)
    for p in permissions_old:
        db.session.delete(p)

    # Getting the new permissions and add them to the database
    for p in permissions:
        new_perm = Permission(description=p, user_id=user_to_update.id)
        db.session.add(new_perm)

    db.session.commit()
    return redirect(url_for("get_users"))


# Delete current user
@app.route('/api/delete/user/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for("get_users"))


# Get permissions for current user
@app.route('/api/permissions/<int:user_id>', methods=['GET'])
def api_get_permissions(user_id):
    all_permissions = Permission.query.filter_by(user_id=user_id)
    output = permissions_schema.dump(all_permissions)
    return jsonify({'user_permissions': output})


# Update permissions for current user
@app.route('/api/update/permissions/<int:user_id>', methods=['PATCH'])
def api_update_permissions(user_id):
    req = request.get_json()
    user_perm_to_update = User.query.get_or_404(user_id)
    permissions = req['permissions']

    if permissions.__contains__('Write'):
        user_perm_to_update.role = 'Editor'
    elif permissions.__contains__('Delete'):
        user_perm_to_update.role = 'Editor'
    else:
        user_perm_to_update.role = 'Viewer'

    db.session.add(user_perm_to_update)
    db.session.commit()

    # Deleting the old permissions
    permissions_old = Permission.query.filter_by(user_id=user_perm_to_update.id)
    for p in permissions_old:
        db.session.delete(p)

    # Getting the new permissions and add them to the database
    for p in permissions:
        new_perm = Permission(description=p, user_id=user_perm_to_update.id)
        db.session.add(new_perm)

    db.session.commit()
    return redirect(url_for("get_users"))


if __name__ == '__main__':
    app.run(debug=True)
