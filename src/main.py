from config import app, qdrant_client, qdrant_host, qdrant_port, API_KEY, api_key_header
import requests
from models import User, Face, DeleteID
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, PointIdsList
import utils
from fastapi import Depends, HTTPException


async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail={"error": 401})


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/get_info")
def get_qdrant_info():
    rq = requests.get(f"http://{qdrant_host}:{qdrant_port}")
    print(rq.json())
    return rq.json()


@app.post("/api/add_user")
async def add_user(user: User, api_key: str = Depends(verify_api_key)):
    registration_id = user.registration_id
    avatar_base64 = user.avatar_base64
    event_id = user.event_id

    embedded_vector = utils.get_embedding(avatar_base64, model=utils.embedding_model)
    if not embedded_vector:
        raise HTTPException(status_code=402, detail={"error": 402})
    elif embedded_vector == 3:
        raise HTTPException(status_code=403, detail={"error": 403})
    try:
        check_score = qdrant_client.search(collection_name='SEARCH_FACE',
                                           query_vector=embedded_vector,
                                           query_filter=Filter(
                                                  must=[
                                                      FieldCondition(
                                                          key="event_id",
                                                          match=MatchValue(value=event_id)
                                                      )
                                                  ]
                                              ),
                                           limit=1,
                                           )
        
        if len(check_score) > 0 and check_score[0].score > 0.65:
            id_ = check_score[0].payload['registration_id']
            raise HTTPException(status_code=407, detail={"error": 407,
                                                         "id": id_})

        response = qdrant_client.upsert(
            collection_name="SEARCH_FACE",
            points=[PointStruct(id=utils.getNumUser(host=qdrant_host,
                                                    port=qdrant_port, collection_name='SEARCH_FACE') + 1,
                                vector=embedded_vector,
                                payload={'registration_id': registration_id,
                                         "avatar_base64": avatar_base64,
                                         "event_id": event_id
                                         })
                    ],
            wait=True
        )

        return {'response': response}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=501, detail={"error": 501})


@app.post("/api/face_recognize")
async def get_similar(face: Face, api_key: str = Depends(verify_api_key)):
    face_base64 = face.avatar_checkin_base64
    event_id = face.event_id
    query_vt = utils.get_embedding(face_base64, model=utils.embedding_model)
    if not query_vt:
        raise HTTPException(status_code=402, detail={"error": 402})
    elif query_vt == 3:
        raise HTTPException(status_code=403, detail={"error": 403})
    try:
        result = qdrant_client.search(collection_name='SEARCH_FACE',
                                      query_vector=query_vt,
                                      query_filter=Filter(

                                          must=[
                                              FieldCondition(
                                                  key="event_id",
                                                  match=MatchValue(value=event_id)
                                              )
                                          ]
                                      ),
                                      limit=1,
                                      )
        if len(result) < 1 or (len(result) > 0 and result[0].score < 0.45):
            raise HTTPException(status_code=406, detail={"error": 406})
        
        return {
                    "id": result[0].payload['registration_id'],
                    'similar_scores': result[0].score,
                    'event_id': result[0].payload['event_id']
                }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=501, detail={"error":501})


@app.post("/api/modify_avatar")
async def modify_avatar(user: User, api_key: str = Depends(verify_api_key)):
    user_id = user.registration_id
    new_avatar = user.avatar_base64
    event_id = user.event_id
    new_vector = utils.get_embedding(image_base64=new_avatar, model=utils.embedding_model)
    if not new_vector:
        raise HTTPException(status_code=402, detail={"error": 402})
    elif new_vector == 3:
        raise HTTPException(status_code=403, detail={"error": 403})
    try:
        # Perform the search
        search_result = qdrant_client.search(
            collection_name="SEARCH_FACE",
            query_vector=new_vector,
            query_filter=Filter(

                must=[
                    FieldCondition(
                        key="registration_id",
                        match=MatchValue(value=user_id),

                    ),
                    FieldCondition(
                         key="event_id",
                         match=MatchValue(value=event_id),
                    )
                ]
            ),
            limit=100

        )

        # Check if the search returned any results
        if not search_result:
            raise HTTPException(status_code=406, detail={"error": 406})

        # Assuming search_result contains a list of points, we take the first one
        id_ = search_result[0].id
        event_id = search_result[0].payload['event_id']
        # Generate new vector embedding

        # Perform the upsert operation
        result = qdrant_client.upsert(
            collection_name="SEARCH_FACE",
            points=[
                PointStruct(
                    id=id_,
                    vector=new_vector,
                    payload={'registration_id': user_id,
                             "avatar_base64": new_avatar, 'event_id': event_id}
                )
            ],
        )

        return {'result': result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=501, detail={"error": 501})


@app.post('/api/delete')
async def delete_user(delete_id: DeleteID, api_key: str = Depends(verify_api_key)):
    verify_id = delete_id.registration_id
    event_id = delete_id.event_id
    arr = [0]*512
    try:
        search_result = qdrant_client.search(
            collection_name="SEARCH_FACE",
            query_vector=arr,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="registration_id",
                        match=MatchValue(value=verify_id)
                    ),
                    FieldCondition(key='event_id', match=MatchValue(value=event_id))
                ]
            ),
            limit=10,

        )
        if not search_result:
            raise HTTPException(status_code=406, detail={"error": 406})

        point_id = search_result[0].id

        result = qdrant_client.delete(
            collection_name="SEARCH_FACE",
            points_selector=PointIdsList(
                points=[point_id],
            ),
        )

        return {'result': result.json()}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=501, detail={"error": 501})
