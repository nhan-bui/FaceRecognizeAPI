import time
import cv2
import numpy as np
import base64
import requests
from insightface.app import FaceAnalysis

embedding_model = FaceAnalysis(name="buffalo_sc", providers=['CUDAExecutionProvider', ])
embedding_model.prepare(ctx_id=0)


def get_embedding(image_base64, model=embedding_model):
    decoded_image = base64.b64decode(image_base64)
    np_arr = np.frombuffer(decoded_image, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    faces = model.get(img)
    embedding = faces[0]['embedding'].tolist()

    return embedding


def getNumUser(host, port, collection_name):
    response = requests.get(f"http://{host}:{port}/collections/{collection_name}")
    if response.status_code == 200:
        collections_info = response.json()

        return collections_info['result']['points_count']

    else:
        return False


if __name__ == '__main__':
    image = cv2.imread("C:/Users/Truongpc/Pictures/Camera Roll/WIN_20220503_15_57_55_Pro.jpg")

    success, encoded_image = cv2.imencode('.png', image)
    image_base64 = base64.b64encode(encoded_image).decode('utf-8')
    # print(image_base64)
    st = time.time()
    a = get_embedding(image_base64)
    ed = time.time()
    print(ed -st)