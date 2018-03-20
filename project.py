from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants/')
def restaurants():
    restaurants = session.query(Restaurant).all()
    output = ""
    output += "<html><body>"
    output += "<p><a href=\"/restaurants/new\">Make a New Restaurant</a></p>"
    for restaurant in restaurants:
        output += "<p>%s</p>" % restaurant.name
        output += "<p><a href='restaurants/%s/edit'>Edit</a></p>" % restaurant.id
        output += "<p><a href='restaurants/%s/delete'>Delete</a></p>" % restaurant.id
        output += "</body></html>"
    return output


@app.route('/restaurants/new')
def new_restaurant():
    output = ""
    output += "<html><body>"
    output += "<form method=\"POST\" enctype = \"multipart/form-data\"" \
              "action=\"/restaurants/new\">" \
              "<h2>New Restaurant Name</h2>" \
              "<input name=\"new-restaurant-name\" type=\"text\" placeholder=\"New restaurant Name\">" \
              "<input type=\"submit\" value=\"Create\"></form>"
    output += "</body></html>"
    return output

@app.route('/restaurants/<int:restaurant_id>/')
def restaurant_menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    # output = ''
    # for i in items:
    #     output += i.name
    #     output += '</br>'
    #     # output += i.price
    #     output += '</br>'
    #     # output += i.description
    #     output += '</br>'
    #     output += '</br>'
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/')
def edit_menu_item(restaurant_id, menu_id):
    return "page to edit a menu item. Task 2 complete!"

# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/')
def delete_menu_item(restaurant_id, menu_id):
    return "page to delete a menu item. Task 3 complete!"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)