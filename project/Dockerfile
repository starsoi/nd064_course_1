# Base image python 3.8
FROM python:3.8

# Copy techtrends folder to /app
COPY techtrends /app

# Expose port 3111
EXPOSE 3111

# Set the working directory to /app
WORKDIR /app

# Install the dependencies
RUN pip install -r requirements.txt

# Intialize the database
RUN python init_db.py

# Run the application
CMD ["python", "app.py"]
