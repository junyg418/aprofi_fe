import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"
token = None

st.title('Aprofi test')


if token is None:
    menu = st.sidebar.selectbox("Menu", ["Register", "Login", "Problem"])
    if menu == "Register":
        st.subheader("Register")
        user_id = st.text_input("user_id")
        password = st.text_input("password", type="password")
        username = st.text_input("username")
        email = st.text_input("email")

        if st.button("submit"):
            data = {
                "user_id": user_id,
                "password": password,
                "username": username,
                "email": email
            }
            response = requests.post(f"{API_URL}/user/register", json=data)
            if response.status_code == 200:
                st.success("User registered successfully!")
            else:
                st.error("failed")

    elif menu == "Login":
        st.subheader("Login")
        user_id = st.text_input("user_id")
        password = st.text_input("password", type="password")

        if st.button("submit"):
            data = {
                "user_id": user_id,
                "password": password
            }
            response = requests.post(f"{API_URL}/user/login", json=data)
            if response.status_code == 200:
                st.success("User Login successful")
                token = response.json()["access_token"]
                print(token)
            else:
                st.error("failed")

# Login 상태
else:
    menu = st.sidebar.selectbox("Menu", ["My Page", "Problem"])

