import logging
import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

error = False

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global error
    try:
        connection = sqlite3.connect('database.db')
    except sqlite3.Error as e:
        error = True
        app.logger.error(f'Database connection error: {e}')
        return None
    error = False
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    global error
    connection = get_db_connection()
    if connection is None:
        return None

    try:
        post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    except sqlite3.Error as e:
        error = True
        app.logger.error(f'Database query error: {e}')
        return None

    error = False
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.logger.setLevel(logging.INFO)

# Define the main route of the web application 
@app.route('/')
def index():
    global error
    connection = get_db_connection()
    try:
        posts = connection.execute('SELECT * FROM posts').fetchall()
    except sqlite3.Error as e:
        error = True
        app.logger.error(f'Database query error: {e}')
    connection.close()
    return render_template('404.html'), 500

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)

    if post is None:
        app.logger.info(f'Article with id "{post_id}" does not exist!')
        return render_template('404.html'), 404
    else:
        app.logger.info('Article "{}" retrieved!'.format(post['title']))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page retrieved!')
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
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info(f'Article "{title}" created!')

            return redirect(url_for('index'))

    return render_template('create.html')

# define a route for health checks
@app.route('/healthz')
def health():
    if not error:
        return jsonify({'result': 'OK - healthy'})
    else:
        return jsonify({'result': 'ERROR - unhealthy'}), 500

# define a route for metrics
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()

    # A Flask app is single threaded, thus the db_connection_count will always be 1
    return jsonify({'db_connection_count': 1, 'post_count': post_count})

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
