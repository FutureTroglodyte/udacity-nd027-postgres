# DROP TABLES

songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# DROP TEMPORARY TABLES

tmp_users_table_drop = "DROP TABLE IF EXISTS tmp_users"
tmp_time_table_drop = "DROP TABLE IF EXISTS tmp_time"

# CREATE TABLES

songplay_table_create = """
    CREATE TABLE IF NOT EXISTS songplays(
       songplay_id SERIAL PRIMARY KEY,
       start_time TIMESTAMP NOT NULL,
       user_id INT NOT NULL,
       level VARCHAR,
       song_id VARCHAR,
       artist_id VARCHAR,
       session_id INT,
       location VARCHAR,
       user_agent VARCHAR
    )
    """

user_table_create = """
    CREATE TABLE IF NOT EXISTS users(
        user_id VARCHAR PRIMARY KEY NOT NULL,
        first_name VARCHAR,
        last_name VARCHAR,
        gender VARCHAR,
        level VARCHAR
    )
    """

song_table_create = """
    CREATE TABLE IF NOT EXISTS songs(
        song_id VARCHAR PRIMARY KEY NOT NULL,
        title VARCHAR NOT NULL,
        artist_id VARCHAR NOT NULL,
        year INT,
        duration FLOAT
    )
    """

artist_table_create = """
    CREATE TABLE IF NOT EXISTS artists(
        artist_id VARCHAR PRIMARY KEY NOT NULL,
        name VARCHAR,
        location VARCHAR,
        latitude VARCHAR,
        longitude VARCHAR
    )
    """

time_table_create = """
    CREATE TABLE IF NOT EXISTS time(
        start_time TIME PRIMARY KEY NOT NULL,
        hour INT,
        day INT,
        week INT,
        month INT,
        year INT,
        weekday INT
    )
    """

# CREATE TEMPORARY TABLES

tmp_user_table_create = """
    CREATE TEMPORARY TABLE IF NOT EXISTS tmp_users(
        user_id VARCHAR PRIMARY KEY NOT NULL,
        first_name VARCHAR,
        last_name VARCHAR,
        gender VARCHAR,
        level VARCHAR
    )
    """

tmp_time_table_create = """
    CREATE TEMPORARY TABLE IF NOT EXISTS tmp_time(
        start_time TIME PRIMARY KEY NOT NULL,
        hour INT,
        day INT,
        week INT,
        month INT,
        year INT,
        weekday INT
    )
    """

# INSERT RECORDS

songplay_table_insert = """
    INSERT INTO songplays(
       start_time,
       user_id,
       level,
       song_id,
       artist_id,
       session_id,
       location,
       user_agent
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

# BULK INSERTS VIA TEMPORARY TABLES

users_table_bulk_insert = """
    INSERT INTO users(
        user_id,
        first_name,
        last_name,
        gender,
        level
    )
    SELECT *
    FROM tmp_users
    ON CONFLICT (user_id)
    DO UPDATE SET level=EXCLUDED.level
    """

time_table_bulk_insert = """
    INSERT INTO time(
        start_time,
        hour,
        day,
        week,
        month,
        year,
        weekday
    )
    SELECT *
    FROM tmp_time
    ON CONFLICT (start_time) DO NOTHING
    """


# FIND SONGS

song_select = """
    SELECT
        s.song_id,
        a.artist_id
    FROM songs AS s
    INNER JOIN artists AS a
        ON s.artist_id = a.artist_id
    WHERE s.title = %s
        AND a.name = %s
        AND s.duration = %s
    """

# QUERY LISTS

create_table_queries = [
    songplay_table_create,
    user_table_create,
    song_table_create,
    artist_table_create,
    time_table_create,
]
drop_table_queries = [
    songplay_table_drop,
    user_table_drop,
    song_table_drop,
    artist_table_drop,
    time_table_drop,
]
