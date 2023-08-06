name="tgFaceRecognition"


import face_recognition
import cv2
import os
import numpy as np
print("Welcon to use TGFaceRecognition, you only need to designate the path of your image folder by use path=path. Then you can run TGFace.TGFace(path) to recognize.")
#imgfolder=None
def TGFace(imgfolder):
    video_capture = cv2.VideoCapture(0)

    # For name to store
    known_person = []

    # For Images
    known_image = []

    # ForEncoding
    known_face_encoding = []

    # Files should be in the Imagefolder folder
    for file in os.listdir(imgfolder):
        try:
            # Extracting person name from the image filename eg:Abhilash.jpg
            known_person.append(str(file).replace(".jpg", ""))

            file = os.path.join(imgfolder, file)
            known_image = face_recognition.load_image_file(file)
            known_face_encoding.append(face_recognition.face_encodings(known_image)[0])
        except Exception as e:
            #print("Not loaded" + str(e))
            pass

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    # process_this_frame = 0
    process_this_frame = 0

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]  #
        #print(process_this_frame)
        # Only process every other frame of video to save time
        if process_this_frame % 3 == 0:
            process_this_frame += 1

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            Length = len(known_face_encoding)
            for face_encoding in face_encodings:
                match = face_recognition.compare_faces(known_face_encoding, face_encoding, tolerance=0.45)
                Matches = np.where(match)[0]  # Checking which image is matched
                if len(Matches) > 0:
                    name = str(known_person[Matches[0]]).replace("1", "")
                    face_names.append(name)
                else:
                    face_names.append("unknow")

        # process_this_frame = not process_this_frame
        process_this_frame += 1

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 1)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), -1)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
