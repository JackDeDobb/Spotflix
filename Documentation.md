### Overview:

Our tool is essentially a recommender system that will provide users with movie recommendations based on the songs that they listen to. We hope to explore the correlation between a user’s song and movie preferences, by comparing song lyrics to movie scripts. This tool is intended for anybody with an interest in both music and movies! 

To acquire the text data, we first retrieve the movie scripts to create a database. We do this by scraping data from IMDB for ~1200 different movies, and store them via . Next, we find the user's top 50 songs on Spotify (with the Spotify API) and retrieve their lyrics (with the Genius API). To rank the movies by their relevance to the songs, we use BM-25. 

### Architecture of the Project:

### Description of Functions:

** App/app.py **

** App/songScraper.py **

** lambdaIntegration.py **



### Usage:

The project requires Celery and Redis Server installed and running locally on the computer. Celery is an aysnchronous task queue and Redis Server is a broker service that Celery relies on to manage those tasks. This was necessary because Flask blocks until all functions return and generating the recommendations take around 20 seconds, this would mean the user sees a blank page for that duration. Using Celery, we were able to create a dynamic progress bar that updates itself every second (through GET requests) while all the song-scraping is done server-side and the scraped lyrics are sent to the AWS REST API. The API allows the server architecture to be light-weight as all computationally expensive tasks are sent to the dedicated AWS Lambda service.

Redis Server can be installed with Homebrew. Flask and Celery can be installed with Pip. Running the app.py file runs the application on the localhost. This is done through Flask's development server. Testing can then be done with the following series of commands:

celery -A app.celery worker --pool solo

(The --pool solo option is necessary because of a bug in macOS)

redis-server

python3 app.py

Navigating to the described url (this is usually part of the output) 
