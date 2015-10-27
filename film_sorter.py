#!/usr/bin/env python

'''
Files and renames your films according to genre
using IMDb API
supert-is-taken 2015
'''

from imdb import IMDb
import sys
import re
import os
import errno
import codecs

db=IMDb()


def main(argv):

    for filename in sys.argv[1:]:
        print filename
        movie_list=db.search_movie( cleanup_movie_string(filename) )
        while len(movie_list) == 0:
            search_string = raw_input('No results, alternative search string: ')
            movie_list = db.search_movie( cleanup_movie_string(search_string) )

        movie=movie_list[0]
        title = movie['long imdb title'].replace('"', "")

        ''' matching is not very reliable so seek confirmation '''
        proceed = raw_input(title + " (Y/n) ")
        if proceed is 'n':
            ix = choose_movie(movie_list)
            while ix == -1:
                search_string = raw_input('Alternative search string: ')
                movie_list = db.search_movie( cleanup_movie_string(search_string) )
                ix = choose_movie(movie_list)
            if ix == -2:
                continue
            movie=movie_list[ix]
            title = movie['long imdb title'].replace('"', "")

        ''' get genres, summary and other extended items '''
        db.update(movie)

        ''' summary to file '''
        with codecs.open(title + ".summary", 'w', "utf-8") as summary:
            summary.write(movie.summary())
            summary.close()

        ''' rename the files and file them '''
        ext = re.search(r'\.[a-zA-Z]*$', filename).group(0)
        for genre in movie['genres']:
            mkdir_p(genre)
            __link(filename, genre + '/' + title + ext)
            __link(filename.replace(ext, ".srt"), genre + '/' + title + ".srt")
            __link(filename.replace(ext, ".sub"), genre + '/' + title + ".srt")
            __link(title + ".summary", genre + '/' + title + ".summary")
            __link(filename.replace(ext, ".idx"), genre + '/' + title + ".idx")
        
        ''' delete old files '''
        __unlink(filename)
        __unlink(title + ".summary")
        __unlink(filename.replace(ext, ".srt"))
        __unlink(filename.replace(ext, ".sub"))
        __unlink(filename.replace(ext, ".idx"))

    return 1


def choose_movie(movie_list):
    print("-2: enter new search string")
    print("-1: enter new search string")
    i=0
    for movie in movie_list:
        prompt = '%d: ' + movie['long imdb title']
        print(prompt % i)
        i+=1
    return int(raw_input("choice: "))


def cleanup_movie_string(s):
    s = s.replace("WEB-DL", "")
    s = re.sub(r'-.*$', "", s)
    s = s.replace(".1.", " ")
    s = s.replace(".0.", " ")
    s = s.replace(".H.", " ")
    s = s.replace(".", " ")
    s = s.replace("mkv", "")
    s = s.replace("X264", "")
    s = s.replace("x264", "")
    s = s.replace("avi", "")
    s = s.replace("mp4", "")
    s = s.replace("720p", "")
    s = s.replace("1080p", "")
    s = s.replace("BluRay", "")
    s = s.replace("Bluray", "")
    s = s.replace("bluray", "")
    s = s.replace("DTS", "")
    s = s.replace("AAC", "")
    s = s.replace("AC3", "")
    s = s.replace("HDTV", "")
    s = s.replace("DD5", "")
    s = s.replace("IMAX", "")
    return s


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


def __link(old, new):
    if os.path.isfile(old):
        try:
            os.link(old, new)
        except:
            pass

def __unlink(filename):
    if os.path.isfile(filename):
        try:
            os.unlink(filename)
        except:
            pass


if __name__=="__main__":
    sys.exit(main(sys.argv))
