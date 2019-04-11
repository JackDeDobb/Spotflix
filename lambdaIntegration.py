"""
    Defines a set of functions that tap into the S3 bucket, look at the user's list of songs
    (the event) variable, and compute a recommendations from the list of movies
    """

import boto3
import json
import math


# The default lambda event
def lambda_handler(event, context):
    
    response = respond(event)
    
    return {
        'statusCode': 200,
        'body': response
    }

# Function that details how a response is processes
def respond(event):
    # Movie_dict is a list of dictionaries that contains a text representation of each movie
    movie_dicts = get_file("movieList.json")
    titles_list = get_file("titleList.json")
    df_dict = get_file("dfDict.json")
    
    song_list = event["songs"]
    
    song_list = prepare_songs(song_list)
    
    response = calculate_movie_score(song_list,movie_dicts,titles_list,df_dict)
    
    return response

# Converts the given list of strings into dicts,num_words
def prepare_songs(song_list):

    new_list = []
    for song in song_list:
        song_dict = {}
        
        for word in song.lower().split():
            if word not in song_dict:
                song_dict[word] = 0
            song_dict[word] += 1

        new_list.append((song_dict,sum(song_dict.values())))

    return new_list

# Opens the S3 bucket and returns a the movie_dicts list
def get_file(key):
    
    movie_dict = {}
    bucket_name = "movie-dicts"
    
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name,key)
    file_content = obj.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    
    return json_content


# Computes the similarity between a movie and a song
def similarity(song,movie,df_dict,total_movie_words,total_song_words,total_movies):

    similarity_score = 0
    
    for key in song:
        if key in movie:
            song_lyric = song[key] / total_song_words
            movie_word = movie[key] / total_movie_words
            log_val = (total_movies + 1) / df_dict[key]
            similarity_score += song_lyric * movie_word * math.log(log_val)
    return similarity_score

# Computes the top 10 movie matches for a given song list
def calculate_movie_score(song_list,movie_list,titles_list,df_dict):
    
    movie_scores = []
    total_movies = len(movie_list)
    
    for idx, movie_dict in enumerate(movie_list):
        acc = 0
        
        for song_dict in song_list:
            total_song_words = song_dict[1]
            song_dict = song_dict[0]
            
            acc += similarity(song_dict, movie_dict,df_dict,titles_list[idx][1],total_song_words,total_movies)
        
        movie_scores.append((acc, titles_list[idx][0]))
    movie_scores.sort()
    
    return [x[1] for x in movie_scores][-10:]
