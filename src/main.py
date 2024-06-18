from config import app, qdrant_client, qdrant_host, qdrant_port
import requests
from models import User, Face, DeleteID
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, PointIdsList
import utils
import numpy as np

idx = utils.getNumUser(qdrant_host, qdrant_port, collection_name='New-search')


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/get_info")
def get_qdrant_info():
    rq = requests.get("http://localhost:6333/")
    print(rq.json())
    return rq.json()


@app.post("/api/add_user")
async def add_user(user: User):
    verify_id = user.verify_id
    avatar_base64 = user.avatar_base64
    embedded_vector = utils.get_embedding(avatar_base64, model=utils.embedding_model)
    try:
        response = qdrant_client.upsert(
            collection_name="SEARCH_FACE",
            points=[PointStruct(id=utils.getNumUser(host=qdrant_host,
                                                    port=qdrant_port, collection_name='SEARCH_FACE') + 1,
                                vector=embedded_vector,
                                payload={'verify_id': verify_id,
                                         "avatar_base64": avatar_base64})
                    ],
            wait=True
        )

        return {'status': 200, 'response': response}
    except Exception as e:
        return {'status': 501, 'error': e}


@app.post("/api/face_recognize")
def get_similar(face: Face):
    face_base64 = face.face_base64
    query_vt = utils.get_embedding(face_base64, model=utils.embedding_model)
    try:
        result = qdrant_client.search(collection_name='SEARCH_FACE',
                                      query_vector=query_vt,
                                      limit=1,
                                      )
        return {'status': 200, "id": result[0].payload['verify_id'], 'scores': result[0].score}
    except Exception as e:
        return {'status': 502, 'error': e}


@app.post("/api/modify_avatar")
def modify_avatar(user: User):
    user_id = user.verify_id
    new_avatar = user.avatar_base64
    try:
        # Perform the search
        search_result = qdrant_client.search(
            collection_name="SEARCH_FACE",
            query_vector=utils.get_embedding(image_base64=new_avatar, model=utils.embedding_model),
            query_filter=Filter(

                must=[
                    FieldCondition(
                        key="verify_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=100

        )

        # Check if the search returned any results
        if not search_result:
            return {'status': 503, 'error': 'User ID not found'}

        # Assuming search_result contains a list of points, we take the first one
        id_ = search_result[0].id

        # Generate new vector embedding
        new_vector = utils.get_embedding(image_base64=new_avatar, model=utils.embedding_model)

        # Perform the upsert operation
        result = qdrant_client.upsert(
            collection_name="SEARCH_FACE",
            points=[
                PointStruct(
                    id=id_,
                    vector=new_vector,
                    payload={'verify_id': user_id, "avatar_base64": new_avatar}
                )
            ],
        )

        return {'status': 200, 'result': result}

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        return {'status': 504, 'error': str(e)}


@app.post('/api/delete')
def delete_user(delete_id: DeleteID):
    verify_id = delete_id.verify_id
    arr = [0]*512
    try:
        search_result = qdrant_client.search(
            collection_name="SEARCH_FACE",
            query_vector=arr,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="verify_id",
                        match=MatchValue(value=verify_id)
                    )
                ]
            ),
            limit=100,

        )
        if not search_result:
            return {'status': 505, 'error': 'User ID not found'}
        point_id = search_result[0].id
        result = qdrant_client.delete(
            collection_name="SEARCH_FACE",
            points_selector=PointIdsList(
                points=[point_id],
            ),
        )
        return {'status': 200, 'result': result.json()}
    except Exception as e:
        return {'status': 506, 'error': e}
