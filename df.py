import zipfile
import os

with zipfile.ZipFile("/Users/corinnefogarty/DS4320/Project-2/data/RDS-2013-0009.6_Data_Format4_SQLITE.zip", "r") as z:
    z.extract("Data/FPA_FOD_20221014.sqlite", "/Users/corinnefogarty/DS4320/Project-2/data/")

print("Extracted. File size:", os.path.getsize("/Users/corinnefogarty/DS4320/Project-2/data/Data/FPA_FOD_20221014.sqlite"))

import sqlite3


conn = sqlite3.connect("/Users/corinnefogarty/DS4320/Project-2/data/Data/FPA_FOD_20221014.sqlite")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(Fires);")
for row in cursor.fetchall():
    print(row)
conn.close()
