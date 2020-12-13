# Udacity Data Engeneering Nanodegree Program

My submission of Project Data Modeling with Postgres

## Summary

The goal of this project is to define fact and dimension tables for a star schema for a particular analytic focus, and write an ETL pipeline that transfers data from files in two local directories into these tables in Postgres using Python and SQL.

### Raw Data

1. \*song_data\*.jsons ('artist_id', 'artist_latitude', 'artist_location',
       'artist_longitude', 'artist_name', 'duration', 'num_songs',
       'song_id', 'title', 'year') - a subset of real data from the [Million Song Dataset](http://millionsongdataset.com/).
2. \*log_data\*.jsons ('artist', 'auth', 'firstName', 'gender', 'itemInSession',
       'lastName', 'length', 'level', 'location', 'method', 'page',
       'registration', 'sessionId', 'song', 'status', 'ts', 'userAgent',
       'userId') - [simulated](https://github.com/Interana/eventsim) activity logs from a music streaming app based on specified configurations.

### Create sparkifydb Postgres Database - Define Fact and Dimension Tables for a Star Schema

Run `python3 create_tables.py` in a terminal to create the Postgres DB containing:

#### A Fact Table

1. songplays (songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent) - records in log data associated with song plays

#### Four Dimension Tables

1. users (user_id, first_name, last_name, gender, level) - users in the app
1. songs (song_id, title, artist_id, year, duration) - songs in music database
1. artists (artist_id, name, location, latitude, longitude) - artists in music database
1. time (start_time, hour, day, week, month, year, weekday) - timestamps of records in songplays broken down into specific units
        
### Run ETL Pipeline

Fill the five star schema tables with data from the raw data jsons by running `python3 etl.py` in a terminal.

## Discuss the Purpose of this Database in the Context of the Startup, Sparkify, and their Analytical Goals.

The startup Sparkify is an audio streaming services provider. "As a freemium service, basic features are free with advertisements and limited control, while additional features, such as offline listening and commercial-free listening, are offered via paid subscriptions. Users can search for music based on artist, album, or genre, and can create, edit, and share playlists." (Taken from [https://en.wikipedia.org/wiki/Spotify](https://en.wikipedia.org/wiki/Spotify))

So the commercial goal is to get as many users as long as possible to use sparkify. In order to achieve this, sparkify must meet/exceed the users expectations and satisfy them. Ways of doing this are
- providing a huge database of artists and songs
- a fancy and usable (Browser, Mobile-App, Desktop-App) GUI
- a good search engine (Analytical goal!)
- a good recommendation system (Analytical goal!)

This database serves the needs of a good recommendation system: The favourite songs of user `X` can easily be extracted of our fact_table given their number_of_plays (by `X`). So we can put users in clusters based on their favourite songs. And if `X` likes the songs `a`, `b`, & `c` and there are other Users in (one of) his cluster(-s) which likes the songs `a`, `b`, `c`, & `d` he also might like song `d`. Let's recommend this song to him. He supposably enjoys that and thus enjoys sparkify.

## State and Justify your Database Schema Design and ETL pipeline.

### Database Schema Design

The denormalized fact table `songplays` provides most information sparkify needs for its basic analytical goals. Reading and aggregation is very fast and if we need additional information from the dimension tables
- `users`
- `artists`
- `songs` (missing genre here 'tho)
- `time`
the joins are very simple -> high readability.

### Create Database and Tables

As all SQL queries are stored in the `sql_queries.py` file, the `create_tables.py` is very compact and readable. It simply contains of four steps:
1. Drop the Postgres DB `sparkifydb`
1. Create the Postgres DB `sparkifydb`
1. Drop all star schema tables
1. Create all star schema tables

### ETL pipeline

As all SQL queries are stored in the `sql_queries.py` file, the `etl.py` is very compact and readable. It can be divided in  steps:
1. Read \*song_data\*.jsons as pd.DataFrame
1. Insert data into `songs` table
1. Insert data into `artists` table
1. Read \*log_data\*.jsons as pd.DataFrame, filtered by "page" == "NextSong"
1. Insert data into `time` table
1. Insert data into `users` table
1. Get `song_id` and `artist_id` from `song` and `artist` tables given a songs `title`, `artist_name` and `length`. It does not work on this small subset as mentioned below.
1. Insert data into `songplays` table


## [Optional] Provide example queries and results for song play analysis.

"Since this is a subset of the much larger dataset, the solution dataset will only have 1 row with values for [...] `songid` and `artistid` in the fact table.", as mentioned [project's rubric](https://review.udacity.com/#!/rubrics/2500/view). A query which orders the songs by their number of plays (which can be seeen as their populartity) like the very simple one here

```
SELECT 
    sp.song_id,
    s.title,
    COUNT(sp.songplay_id) AS num_of_plays
FROM songplays AS sp
INNER JOIN songs AS s
ON sü.song_id = s.song_id
GROUP BY
    sp.song_id,
    s.title
ORDER BY COUNT(sp.songplay_id)
```

does not work.

To be more precise, queries regarding either songs or artists unfortunately do not provide any results for song play analysis on this database.

All we can do is some user analysis over time like:

```
SELECT
    sp.user_id,
    u.last_name,
    u.first_name,
    t.year,
    t.month,
    t.day,
    -- t.hour,
    210 * COUNT(sp.songplay_id) AS time_spent,
FROM songplays AS sp
INNER JOIN users AS U
    ON sp.user_id = u.user_id
INNER JOIN time AS t
    ON sp.start_time = t.start_time
GROUP BY
    sp.user_id,
    u.last_name,
    u.first_name,
    t.year,
    t.month,
    t.day
    -- , t.hour
ORDER BY
    sp.user_id,
    u.last_name,
    u.first_name,
    t.year,
    t.month,
    t.day
    -- , t.hour
```

Under the assumtions that
- an average song has a length of 210 sec
- the useer does not skip/stop any songs,

it gives the time (in sec) users are spending on sparkify for each day (resp. each hour).
