# Imports
# The first line says that we'll use Flask to render a template, redirecting to another url, and creating a URL
from flask import Flask, render_template, redirect, url_for
# The second line says we'll use PyMongo to interact with our Mongo database
from flask_pymongo import PyMongo
# The third line says that to use the scraping code, we will convert from Jupyter notebook to Python
import scraping
# Flask setup
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
#tells Python that our app will connect to Mongo using a URI, a uniform resource identifier similar to a URL
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# First, let's define the route for the HTML page
# This route tells flask what to display when we're looking at the homepage (index.html)
# This function is what links our visual representation of our work, our web app, to the code that powers it
@app.route("/")
def index():
   # uses PyMongo to find the "mars" collection in our database  
   mars = mongo.db.mars.find_one()
   # mars=mars tells python to use the "mars" collection in MongoDB
   return render_template("index.html", mars=mars)

# Our next function will set up our scraping route
# This route will be the "button" of the web application, the one that will scrape updated data when we tell it to from the homepage of our web app
# The first line, @app.route(“/scrape”) defines the route that Flask will be using
@app.route("/scrape")
# The next lines allow us to access the database, scrape new data using our scraping.py script, update the database, and return a message when successful.
def scrape():
   # we assign a new variable that points to our Mongo database
   mars = mongo.db.mars
   # we create a new variable to hold the newly scraped data
   # In this line, we're referencing the scrape_all function in the scraping.py file exported from Jupyter Notebook
   mars_data = scraping.scrape_all()
   # Now that we've gathered new data, we need to update the database using .update_one()
   mars.update_one({}, {"$set":mars_data}, upsert=True)
   # Finally, we will add a redirect after successfully scraping the data: return redirect('/', code=302). This will navigate our page back to / where we can see the updated content.
   return redirect('/', code=302)

# Telling flask to run
if __name__ == "__main__":
   app.run()