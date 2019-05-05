### OVERVIEW
Our tool is essentially a recommender system that will provide users with movie recommendations based on the songs that they listen to. We hope to explore the correlation between a user’s song and movie preferences, by comparing song lyrics to movie scripts. This tool is intended for anybody with an interest in both music and movies! 

To acquire the text data, we first retrieve the movie scripts to create a database. We do this by scraping data from IMDB for ~1200 different movies, and store them via ______. Next, we find the user's top 50 songs on Spotify (with the Spotify API) and retrieve their lyrics (with the Genius API). To rank the movies by their relevance to the songs, we use BM-25. 
