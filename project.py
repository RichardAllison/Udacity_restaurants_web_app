from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from flask import session as login_session
# import random
# import string

app = Flask(__name__)
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
# @app.route('/login/')
# def showLogin():
#     state = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                     for x in xrange(32))
#     login_session['state'] = state
#     # return "The current session state is %s" % login_session['state']
#     return render_template('login.html')


@app.route('/restaurants/')
def restaurants():
    restaurants = session.query(Restaurant).all()
    output = ""
    output += "<html><body>"
    output += "<p><a href=\"/restaurants/new\">Make a New Restaurant</a></p>"
    for restaurant in restaurants:
        output += "<p><a href=/restaurants/%s>%s</a></p>" % (restaurant.id, restaurant.name)
        output += "<p><a href='/restaurants/%s/edit'>Edit</a></p>" % restaurant.id
        output += "<p><a href='/restaurants/%s/delete'>Delete</a></p>" % restaurant.id
        output += "</body></html>"
    return output


@app.route('/restaurants/new/', methods=['GET', 'POST'])
def new_restaurant():
    if request.method == 'POST':
        new_restaurant = Restaurant(name=request.form['new-restaurant'])
        session.add(new_restaurant)
        session.commit()
        return redirect(url_for('restaurants'))
    else:
        output = ""
        output += "<html><body>"
        output += "<form method=\"POST\" enctype = \"multipart/form-data\"" \
              "action=\"/restaurants/new/\">" \
              "<h2>New Restaurant</h2>" \
              "<input name=\"new-restaurant\" type=\"text\" placeholder=\"New restaurant\">" \
              "<input type=\"submit\" value=\"Create\"></form>"
        output += "</body></html>"
        return output


@app.route('/restaurants/<int:restaurant_id>/')
def restaurant_menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'], restaurant_id=restaurant_id, price=request.form['price'],
                            course=request.form['course'], description=request.form['description'])
        session.add(new_item)
        session.commit()
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    restaurant_to_edit = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['edit-restaurant-name']:
            restaurant_to_edit.name = request.form['edit-restaurant-name']
        session.add(restaurant_to_edit)
        session.commit()
        return redirect(url_for('restaurants'))
    else:
        return render_template('editrestaurant.html', restaurant=restaurant_to_edit)


@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    restaurant_to_delete = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant_to_delete)
        session.commit()
        return redirect(url_for('restaurants'))
    else:
        return render_template('deleterestaurant.html', restaurant=restaurant_to_delete)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def menu_item_JSON(restaurant_id, menu_id):
    menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=menu_item.serialize)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
    edited_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edited_item.name = request.form['name']
        session.add(edited_item)
        session.commit()
        flash("Menu Item has been edited")
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, i=edited_item)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
    delete_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(delete_item)
        session.commit()
        flash("Menu Item has been deleted")
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=delete_item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)