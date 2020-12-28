import os
from io import StringIO
import glob
import psycopg2
import pandas as pd

from sql_queries import *

def copy_from_dataframe(cursor, df, table) -> None:
    """
    Here we are going save the dataframe in memory 
    and use copy_from() to copy it to the table

    Code ist taken from
    https://naysan.ca/2020/06/21/pandas-to-postgresql-using-psycopg2-copy_from/
    """
    # save dataframe to an in memory buffer
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    
    try:
        cursor.copy_from(buffer, table, sep=",")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)


def process_song_file(cur, filepath):
    """
    1. Read \*song_data\*.jsons as pd.DataFrame
    2. Insert data into `songs` table
    3. Insert data into `artists` table
    """
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = df[["song_id", "title", "artist_id", "year", "duration"]]
    copy_from_dataframe(cursor=cur, df=song_data, table="songs")

    # insert artist record
    artist_data = df[
        [
            "artist_id",
            "artist_name",
            "artist_location",
            "artist_latitude",
            "artist_longitude",
        ]
    ]
    copy_from_dataframe(cursor=cur, df=song_data, table="artists")


def process_log_file(cur, filepath):
    """
    1. Read \*log_data\*.jsons as pd.DataFrame, filtered by "page" == "NextSong"
    2. Insert data into `time` table
    3. Insert data into `users` table
    4. Get `song_id` and `artist_id` from `song` and `artist` tables given a songs `title`, `artist_name` and `length`.
    5. Insert data into `songplays` table
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df["page"] == "NextSong"]

    # convert timestamp column to datetime
    t = pd.to_datetime(df["ts"], unit="ms")

    # insert time data records
    time_df = pd.concat(
        [
            t.dt.time,
            t.dt.hour,
            t.dt.day,
            t.dt.week,
            t.dt.month,
            t.dt.year,
            t.dt.weekday,
        ],
        axis=1,
    )
    time_df.columns = [
        "start_time",
        "hour",
        "day",
        "week_of_year",
        "month",
        "year",
        "weekday",
    ]
    time_df = time_df.drop_duplicates(subset="start_time")

    # for i, row in time_df.iterrows():
    #     cur.execute(time_table_insert, list(row))
    copy_from_dataframe(cursor=cur, df=time_df, table="time")
    # TODO: fix the conflicts with duplicates.


    # load user table
    user_df = df[["userId", "firstName", "lastName", "gender", "level"]]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():

        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (
            row.ts,
            row.userId,
            row.level,
            songid,
            artistid,
            row.sessionId,
            row.location,
            row.userAgent,
        )
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
    Read raw_date insert it into star schema tables

    A wrapper for process_song_file & process_log_file (= func).
    Applying them to every .json file in every sub-directory of filepath.
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, "*.json"))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print("{} files found in {}".format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print("{}/{} files processed.".format(i, num_files))


def main():
    """
    01. Establishes connection with the sparkify database and gets cursor to it
    02. Read \*song_data\*.jsons as pd.DataFrame
    03. Insert data into `songs` table
    04. Insert data into `artists` table
    05. Read \*log_data\*.jsons as pd.DataFrame, filtered by "page" == "NextSong"
    06. Insert data into `time` table
    07. Insert data into `users` table
    08. Get `song_id` and `artist_id` from `song` and `artist` tables given a songs `title`, `artist_name` and `length`. It does not work on this small subset as mentioned below.
    09. Insert data into `songplays` table
    10. Finally, closes the connection
    """
    conn = psycopg2.connect(
        "host=127.0.0.1 dbname=sparkifydb user=student password=student"
    )
    cur = conn.cursor()

    process_data(cur, conn, filepath="data/song_data", func=process_song_file)
    process_data(cur, conn, filepath="data/log_data", func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()
