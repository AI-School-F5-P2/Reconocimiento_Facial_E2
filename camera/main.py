import asyncio
import locale
import os
import pickle
import time
from datetime import datetime

import cv2
import cvzone
import face_recognition
import firebase_admin
import numpy as np
from firebase_admin import credentials, db, storage
from encoder import encoder
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL")
storage_url = os.getenv("STORAGE_URL")

async def initialize_firebase():
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

    cred = credentials.Certificate("./ComputerVision/config/database/secret_key_example.json")
    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": database_url,
            "storageBucket": storage_url,
        },
    )


async def get_employee_info(id):
    ref = db.reference(f"Employees/{id}/")
    employeeInfo = ref.get()

    return employeeInfo


async def get_image(id, bucket):
    blob = bucket.blob(f"images/{id}.png")
    array = np.frombuffer(blob.download_as_string(), np.uint8)
    img = cv2.imdecode(array, cv2.IMREAD_COLOR)

    return img


async def main():
    await initialize_firebase()
    bucket = storage.bucket()
    await encoder(bucket)

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    imgBackground = cv2.imread("resources/background.png")

    # Import the mode images
    folderPath = "resources/modes/"
    pathList = os.listdir(folderPath)
    imgList = []

    for path in pathList:
        img = cv2.imread(f"{folderPath}{path}")
        imgList.append(img)

    # Load the encodings
    file = open("encodings.p", "rb")
    encodeListWithId = pickle.load(file)
    file.close()
    encodeListKnown, employeeIds = zip(*encodeListWithId)

    modeType = 0
    counter = 0
    id = -1
    imgEmployee = []

    while True:
        success, img = cap.read()

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        imgBackground[162 : 162 + 480, 55 : 55 + 640] = img

        if modeType is not None and 0 <= modeType < len(imgList):
            if modeType == 1:
                imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgList[modeType]
                time.sleep(0.5)
            imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgList[modeType]
        else:
            print("Error: modeType no es un índice válido.")

        if faceCurFrame:
            for encoFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encoFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encoFace)
                matchIndex = faceDis.argmin()
                confidence = (1 - faceDis[matchIndex]) * 100

                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = 4 * y1, 4 * x2, 4 * y2, 4 * x1
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(
                        imgBackground, bbox, 20, t=3, rt=0, colorC=(255, 246, 238)
                    )

                    id = employeeIds[matchIndex]
                    if counter == 0:
                        cv2.imshow("Face Attendance", imgBackground)
                        counter = 1
                        modeType = 1

            if counter != 0:
                if counter == 1:
                    employeeInfo = await get_employee_info(id)
                    imgEmployee = await get_image(id, bucket)

                    dateObject = datetime.strptime(
                        employeeInfo["last_attendance"], "%Y-%m-%d %H:%M:%S"
                    )

                    elapsed_time = (datetime.now() - dateObject).total_seconds()

                    if elapsed_time > 30:
                        ref = db.reference(f"Employees/{id}/")
                        employeeInfo["total_attendance"] += 1
                        ref.child("total_attendance").set(
                            employeeInfo["total_attendance"]
                        )
                        ref.child("last_attendance").set(
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgList[
                            modeType
                        ]

                if modeType != 3:
                    if 10 < counter < 20:
                        modeType = 2

                    imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgList[modeType]

                    if counter <= 10:
                        cv2.putText(
                            imgBackground,
                            str(employeeInfo["total_attendance"]),
                            (861, 125),
                            cv2.FONT_HERSHEY_PLAIN,
                            1.5,
                            (48, 65, 84),
                            2,
                        )

                        cv2.putText(
                            imgBackground,
                            str(confidence)[:5] + "%",
                            (961, 125),
                            cv2.FONT_HERSHEY_PLAIN,
                            1.5,
                            (48, 65, 84),
                            2,
                        )

                        cv2.putText(
                            imgBackground,
                            str(employeeInfo["position"]),
                            (935, 493),
                            cv2.FONT_HERSHEY_PLAIN,
                            1.5,
                            (48, 65, 84),
                            2,
                        )

                        cv2.putText(
                            imgBackground,
                            str(f"ID: {id}"),
                            (935, 600),
                            cv2.FONT_HERSHEY_PLAIN,
                            1.5,
                            (48, 65, 84),
                            2,
                        )

                        cv2.putText(
                            imgBackground,
                            str(employeeInfo["department"]),
                            (975, 550),
                            cv2.FONT_HERSHEY_PLAIN,
                            1.5,
                            (48, 65, 84),
                            2,
                        )

                        formatted_date = datetime.strptime(
                            employeeInfo["last_attendance"], "%Y-%m-%d %H:%M:%S"
                        ).strftime("%d de %B de %Y")

                        cv2.putText(
                            imgBackground,
                            formatted_date,
                            (848, 650),
                            cv2.FONT_HERSHEY_PLAIN,
                            1.5,
                            (48, 65, 84),
                            2,
                        )

                        (w, h), _ = cv2.getTextSize(
                            str(employeeInfo["name"]),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            2,
                        )

                        offset = (414 - w) // 2

                        cv2.putText(
                            imgBackground,
                            str(employeeInfo["name"]),
                            (808 + offset, 445),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (25, 75, 231),
                            2,
                        )

                        imgBackground[175 : 175 + 216, 909 : 909 + 216] = imgEmployee
                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        employeeInfo = []
                        imgEmployee = []
                        imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgList[
                            modeType
                        ]
        else:
            modeType = 0
            counter = 0

        cv2.imshow("Face Attendance", imgBackground)
        cv2.waitKey(1)


if __name__ == "__main__":
    asyncio.run(main())
