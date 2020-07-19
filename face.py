from PIL import Image,ImageDraw, ImageFont
import face_recognition
import numpy as np
import cv2
from config import config    #importing config from config package
import snowflake.connector as sf
import array
#----------------------------------------------------------------------------------------
#For Video Capture
video_capture = cv2.VideoCapture(0)
#----------------------------------------------------------------------------------------
#Creating the connection and Setup
conn = sf.connect (user=config.username, password=config.password, account=config.account)

def execute_query (connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    cursor.close()

try:
    sql = 'use {}'.format (config.database)
    execute_query (conn, sql)

    sql = 'use warehouse {}'.format (config.warehouse)
    execute_query (conn, sql)

    try:
        sql = 'alter warehouse {} resume'.format(config.warehouse)
        execute_query (conn, sql)
    except:
        pass

except Exception as e:
    print(e)
#----------------------------------------------------------------------------------------
#For dynamically loading the image list from snowflake database
sql = "select image from users"
cursor = conn.cursor()
cursor.execute(sql)

users_image = []
users_face_encoding = []
known_face_encodings = []
known_face_names = []

for a in cursor:
    z = face_recognition.load_image_file(a[0])
    users_image.append(z)
    users_face_encoding.append(face_recognition.face_encodings(z)[0])

for s in users_face_encoding:
    known_face_encodings.append(s)

sql = "select name from users"
cursor = conn.cursor()
cursor.execute(sql)
for c in cursor:
    known_face_names.append(c[0])

#----------------------------------------------------------------------------------------
#Face Recognition Routine
while True:
    ret, frame = video_capture.read()

    rgb_frame = frame[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # loop through each face in this frame of video
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown Person"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        cv2.rectangle(frame, (left , bottom - 120 ), (right , bottom ), (0, 0, 255), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom ), font, 0.7, (255, 255, 255), 1)
        if (name != "Unknown Person"):
            print(name, "was here")
    cv2.imshow('Video', frame)

    # Q to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#----------------------------------------------------------------------------------------
