import streamlit as st
import requests
import base64

API_URL = "http://localhost:8080"


def add_user(verify_id, avatar_base64):
    url = f"{API_URL}/api/add_user"
    data = {"verify_id": verify_id, "avatar_base64": avatar_base64}
    response = requests.post(url, json=data)
    return response.json()


def modify_avatar(verify_id, avatar_base64):
    url = f"{API_URL}/api/modify_avatar"
    data = {"verify_id": verify_id, "avatar_base64": avatar_base64}
    response = requests.post(url, json=data)
    return response.json()


def delete_user(verify_id):
    url = f"{API_URL}/api/delete"
    data = {"verify_id": verify_id}
    response = requests.post(url, json=data)
    return response.json()


def face_recognize(face_base64):
    url = f"{API_URL}/api/face_recognize"
    data = {"face_base64": face_base64}
    response = requests.post(url, json=data)
    return response.json()


def file_to_base64(file):
    return base64.b64encode(file.read()).decode()


st.title("User Management")

st.sidebar.title("Actions")
action = st.sidebar.radio("Select Action", ["Add User", "Modify Avatar", "Delete User", "Face Recognize"])

if action == "Add User":
    st.header("Add User")
    verify_id = st.text_input("Verify ID")
    avatar_file = st.file_uploader("Upload Avatar", type=["jpg", "jpeg", "png"])

    if st.button("Add User"):
        if verify_id and avatar_file:
            avatar_base64 = file_to_base64(avatar_file)
            response = add_user(verify_id, avatar_base64)
            st.write(response)
        else:
            st.error("Please provide Verify ID and upload an avatar.")

elif action == "Modify Avatar":
    st.header("Modify Avatar")
    verify_id = st.text_input("Verify ID")
    new_avatar_file = st.file_uploader("Upload New Avatar", type=["jpg", "jpeg", "png"])

    if st.button("Modify Avatar"):
        if verify_id and new_avatar_file:
            avatar_base64 = file_to_base64(new_avatar_file)
            response = modify_avatar(verify_id, avatar_base64)
            st.write(response)
        else:
            st.error("Please provide Verify ID and upload a new avatar.")

elif action == "Delete User":
    st.header("Delete User")
    verify_id = st.text_input("Verify ID")

    if st.button("Delete User"):
        if verify_id:
            response = delete_user(verify_id)
            st.write(response)
        else:
            st.error("Please provide Verify ID.")

elif action == "Face Recognize":
    st.header("Face Recognize")
    face_file = st.file_uploader("Upload Face Image", type=["jpg", "jpeg", "png"])

    if st.button("Recognize Face"):
        if face_file:
            face_base64 = file_to_base64(face_file)
            response = face_recognize(face_base64)
            st.write(response)
        else:
            st.error("Please upload a face image.")
