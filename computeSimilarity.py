import math

# Computes a similarity score based on tf-idf between a movie and a song
def tfidf_similarity(song, movie, df_dict, total_movie_words, total_song_words):
    similarity_score = 0
    for key in song:
        if key in movie:
            song_lyric = song[key] / total_song_words
            movie_word = movie[key] / total_movie_words
            log_val = (total_movies + 1) / df_dict[key]
            similarity_score += song_lyric * movie_word * math.log(log_val)
    return similarity_score

# Computes a similarity score based on bm25 between a movie and a song
def bm25_similarity(song, movie, df_dict, total_movie_words, total_song_words, k1, b, k3):
    similarity_score = 0
    for key in song:
        if key in movie:
            song_lyric = song[key] / total_song_words
            movie_word = movie[key] / total_movie_words
            log_val = (total_movies + 1) / df_dict[key]
            numerator = song_lyric * movie_word * math.log(log_val) * (k + 1)
            denominator = movie_word + (k * (1 - b + (b * (total_movie_words / avdl))))
            similarity_score += (numerator / denominator)
    return similarity_score


# Computes the top 10 movie matches for a given song list
def calculate_movie_score(song_list, movie_list, titles_list, df_dict):
    movie_scores = []
    for idx, movie_dict in enumerate(movie_list):
        acc = 0
        for song_dict in song_list:
            total_song_words = song_dict[1]
            song_dict = song_dict[0]
            acc += tfidf_similarity(song_dict, movie_dict, df_dict, titles_list[idx][1], total_song_words)
        movie_scores.append((acc, title_list[idx][0]))
    movie_scores.sort()
    return [x[1] for x in movie_scores][-10:]
