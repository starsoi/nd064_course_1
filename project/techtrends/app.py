import logging
import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

num_connection = 0

class DbConnection:
    def __enter__(self):
        global num_connection
        self._conn = self._get_db_connection()
        if self._conn:
            num_connection += 1
            return self._conn

    def __exit__(self, *exc_details):
        global num_connection
        if self._conn:
            num_connection -=1
            self._conn.close()

    # Function to get a database connection.
    # This function connects to database with the name `database.db`
    def _get_db_connection(self):
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        return connection

# Function to get a post using its ID
def get_post(post_id):
    with DbConnection() as connection:
        post = connection.execute('SELECT * FROM posts WHERE id = ?',
                            (post_id,)).fetchone()
        return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.logger.setLevel(logging.DEBUG)

# Define the main route of the web application 
@app.route('/')
def index():
    with DbConnection() as connection:
        posts = connection.execute('SELECT * FROM posts').fetchall()
        return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)

    if post is None:
        app.logger.debug(f'Article with id "{post_id}" does not exist!')
        return render_template('404.html'), 404
    else:
        app.logger.debug('Article "{}" retrieved!'.format(post['title']))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.debug('About Us page retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            with DbConnection() as connection:
                connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                             (title, content))
                connection.commit()

                app.logger.debug(f'Article "{title}" created!')

            return redirect(url_for('index'))

    return render_template('create.html')

# define a route for health checks
@app.route('/healthz')
def health():
    app.logger.debug(f'Health status retrieved!')
    return jsonify({'result': 'OK - healthy'})

# define a route for metrics
@app.route('/metrics')
def metrics():
    global num_connection
    with DbConnection() as connection:
        post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]

    # A Flask app is single threaded, thus the db_connection_count will always be 1
    app.logger.debug('Current metrics revtried!')
    return jsonify({'db_connection_count': num_connection, 'post_count': post_count})

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
