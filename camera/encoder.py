import os
import pickle

import cv2
import face_recognition
import time

def read_images(bucket):
    os.system("clear")
    print(f"Conectando al storage...\n")

    
    folderPath = "images/"
    pathList = os.listdir(folderPath)
    imgList = []
    employeeIds = []

    for path in pathList:
        img = cv2.imread(f"{folderPath}{path}")
        
        if img is not None:
            imgList.append(img)
            employeeIds.append(os.path.splitext(path)[0])
            print(f"Leyendo imagen {path}")
            fileName = f"{folderPath}{path}"
            blob = bucket.blob(fileName)
            blob.upload_from_filename(fileName)
        else:
            print(f"Error: No se pudo leer la imagen {path}")
            
    return imgList, employeeIds


def findEncodings(imgList, employeeIds):
    encodeList = []
    os.system("clear")
    time.sleep(1)
    for img, emp_id in zip(imgList, employeeIds):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
        print(f"Codificando imagen para empleado {emp_id}")

    return encodeList

async def encoder(bucket):
    imgList, employeeIds = read_images(bucket)
    encodeList = findEncodings(imgList, employeeIds)

    encodeListWithId = []
    for encode, id in zip(encodeList, employeeIds):
        encodeListWithId.append([encode, id])

    file = open("encodings.p", "wb")
    pickle.dump(encodeListWithId, file)
    file.close()
    print()
    print(f"Encoding finalizado. Archivo encodings.p creado.")

if __name__ == "__main__":
    encoder()
