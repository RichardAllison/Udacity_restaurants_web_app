from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi

from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WebserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>Hello!"
                output += "<form method=\"POST\" enctype = \"multipart/form-data\" action=\"/hello\"><h2>What would you like me to say?</h2><input name=\"message\" type=\"text\"><input type=\"submit\"></form>"
                output += "</body></html>"
                self.wfile.write(bytes(output, "utf8"))
                print(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<form method=\"POST\" enctype = \"multipart/form-data\"" \
                          "action=\"/restaurants/new\">" \
                          "<h2>New Restaurant Name</h2>" \
                          "<input name=\"new-restaurant-name\" type=\"text\" placeholder=\"New restaurant Name\">" \
                          "<input type=\"submit\" value=\"Create\"></form>"
                output += "</body></html>"
                self.wfile.write(bytes(output, "utf8"))
                print(output)
                return


            if self.path.endswith("/edit"):
                restaurant_ID_path = self.path.split("/")[2]
                my_restaurant_query = session.query(Restaurant).filter_by(id=restaurant_ID_path).one()
                if my_restaurant_query != []:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    output = "<html><body>"
                    output += "<form method=\"POST\" enctype = \"multipart/form-data\"" \
                          "action=\"/restaurants/%s/edit\">" % restaurant_ID_path
                    output += "<h2>Edit Restaurant Name</h2>" \
                          "<input name=\"new-restaurant-name\" type=\"text\" placeholder=\"%s\">" % my_restaurant_query.name
                    output += "<input type=\"submit\" value=\"Rename\"></form>"
                    output += "</body></html>"
                    self.wfile.write(bytes(output, "utf8"))
                    print(output)
                    return

            if self.path.endswith("/delete"):
                restaurant_ID_path = self.path.split("/")[2]
                my_restaurant_query = session.query(Restaurant).filter_by(id=restaurant_ID_path).one()
                if my_restaurant_query != []:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    output = "<html><body>"
                    output += "<form method=\"POST\" enctype = \"multipart/form-data\"" \
                          "action=\"/restaurants/%s/delete\">" % restaurant_ID_path
                    output += "<h2>Delete Restaurant</h2>"
                    output += "<input type=\"submit\" value=\"Delete\"></form>"
                    output += "</body></html>"
                    self.wfile.write(bytes(output, "utf8"))
                    print(output)
                    return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = session.query(Restaurant).all()
                output = ""
                output += "<html><body>"
                output += "<p><a href=\"/restaurants/new\">Make a New Restaurant</a></p>"
                for restaurant in restaurants:
                    output += "<p>%s</p>" % restaurant.name
                    output += "<p><a href='restaurants/%s/edit'>Edit</a></p>" % restaurant.id
                    output += "<p><a href='restaurants/%s/delete'>Delete</a></p>" % restaurant.id
                    output += "</body></html>"
                self.wfile.write(bytes(output, "utf8"))
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)


                    messagecontent = fields.get('new-restaurant-name')
                    restaurant_ID_path = self.path.split("/")[2]
                    my_restaurant_query = session.query(Restaurant).filter_by(id=restaurant_ID_path).one()

                    if my_restaurant_query != []:
                        my_restaurant_query.name = messagecontent[0].decode("utf-8")
                        session.add(my_restaurant_query)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

                restaurant_ID_path = self.path.split("/")[2]
                my_restaurant_query = session.query(Restaurant).filter_by(id=restaurant_ID_path).one()

                if my_restaurant_query != []:
                    session.delete(my_restaurant_query)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('new-restaurant-name')

                    new_restaurant = Restaurant(name=messagecontent[0].decode("utf-8"))
                    session.add(new_restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()


            if self.path.endswith("/hello"):
                self.send_response(301)
                self.end_headers()
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                    output = ""
                    output += "<html><body>"
                    output += "<h2>Okay, how about this: </h2>"
                    output += "<h1>%s</h1>" % messagecontent[0].decode("utf-8")
                    output += "<form method=\"POST\" enctype=\"multipart/form-data\" action=\"/hello\"><h2>What would you like me to say?</h2><input name=\"message\" type=\"text\"><input type=\"submit\"></form>"
                    output += "</body></html>"
                    self.wfile.write(bytes(output, "utf8"))
                    print(output)

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebserverHandler)
        print("Web server running on port %s" % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print("")


if __name__ == '__main__':
    main()
