import psycopg
from invisible_watermark_detext import invis_test
import os
# Connect to PostgreSQL
conn = psycopg.connect(dbname="watermark", user="postgres", password="shive", host="localhost")
cur = conn.cursor()
# Create table

#cur.execute("""
#CREATE TABLE images (
#    id SERIAL PRIMARY KEY,
#    link TEXT,
#    data BYTEA,
#    lsb_val double precision,
#    dct_energy double precision,
#    watermarked Boolean
#)
#""")
#conn.commit()
for file in os.listdir(r'D:\watermark_detect\valid\watermark'):
    f=os.path.join(r'D:\watermark_detect\valid\watermark',file)
    
    i,j=invis_test(f)
# Insert image
    with open(f, "rb") as data:
        img_bytes = data.read()

    cur.execute("INSERT INTO images2 (link, data, lsb_val, dct_energy,watermarked) VALUES (%s, %s,%s,%s,%s)", (f, psycopg.Binary(img_bytes),i,j,True))
    conn.commit()





cur.close()
conn.close()
