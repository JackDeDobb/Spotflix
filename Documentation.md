### Overview:

Our tool is essentially a recommendation system that will provide users with movie recommendations based on the songs that they listen to. We hope to explore the correlation between a user’s song and movie preferences, by comparing song lyrics to movie scripts. This tool is intended for anybody with an interest in both music and movies!

To acquire the text data, we first retrieved the movie scripts to create a database. We did this by scraping data from IMsDB for ~1200 different movies, and stored them in an Amazon Web Services (AWS) S3 bucket. Next, we find the user's top 50 songs on Spotify (with the Spotify API) and retrieve their lyrics (with the Genius API). To rank the movies by their relevance to the songs, we use the TF-IDF ranking function.

### Architecture of the Project:

The project relies on the AWS Lambda service to generate the recommendations themselves. The application itself is built using Python and Flask. The Lambda service allowed us to create a REST API that responds to post requests containing a list of song lyrics. The movie-script database is stored on an S3 bucket but because the song lyrics list is quite dynamic, we have to parse those in real-time, server-side. The code to generate recommendations is part of a AWS Lambda function. This ensures that all computationally involved tasks are done server-side, making our project quite portable.

### Description of Functions:2

** App/ **

This directory contains the definitions for the actual web-interface. This is built using Flask. App.py contains the various routes and Celery integration that manage the various URLs. songScraper.py contains a set of helper methods that accept a list of song titles as input and retrieve their corresponding lyrics through the Genius API. These lyrics are then sent to the AWS Lambda function through a POST requests that then responds with the recommendations for a user.

** lambdaIntegration.py **

This file contains the definitions of the components of the AWS Lambda function. The Lambda function accepts a list of song lyrics, uses TF-IDF to compute similarities and rank movies, it then returns a list of the top-matches along with relevant metadata. The components also communicate with the S3 bucket to import the movie-script data that we have parsed and stored. 

** movieScraper.py **

This file contains the code we used to scrape the IMsDB database. The code uses Beautiful Soup to scrape relevant urls, retrieve scripts, and meta-data. It then uses the Boto3 library to store the data in the S3 bucket we've configured for the project.

### Usage:

The project requires Celery and Redis Server installed and running locally on the computer. Celery is an aysnchronous task queue and Redis Server is a broker service that Celery relies on to manage those tasks. This was necessary because Flask blocks until all functions return and generating the recommendations take around 20 seconds, this would mean the user sees a blank page for that duration. Using Celery, we were able to create a dynamic progress bar that updates itself every second (through GET requests) while all the song-scraping is done server-side and the scraped lyrics are sent to the AWS REST API. The API allows the server architecture to be light-weight as all computationally expensive tasks are sent to the dedicated AWS Lambda service.

Redis Server can be installed with Homebrew. Flask and Celery can be installed with Pip. Running the app.py file runs the development server on the localhost. This is done through Flask's development server. Testing can then be done with the following series of commands upon navigating to the App/ folder in the repository:

celery -A app.celery worker --pool solo

(The --pool solo option is necessary because of a bug in macOS)

redis-server

python3 app.py

Navigating to the described url (this is usually part of the output) will prompt a Spotify login. Upon login, the user is directed to a simple page that displays a progress bar and once the recommendations are generated, it displays a table of recommendations that lists movie titles, genre, a cover, release-date, and rating.
