import streamlit as st
import requests

API_URL = "http://210.115.227.15:8000"
if "token" not in st.session_state:
    st.session_state.token = None

st.title('Aprofi test')


if st.session_state.token is None:
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
                st.session_state.token = response.json()["access_token"]
                st.experimental_rerun()
                print(st.session_state.token)
            else:
                st.error("failed")

    elif menu == "Problem":
        pass


# Login 상태
if st.session_state.token:
    menu = st.sidebar.selectbox("Menu", ["MyPage", "Problem"])
    if menu == "MyPage":
        request_header = {
            "Authorization": f"Bearer {st.session_state.token}"
        }
        user_info = requests.get(f"{API_URL}/user/me/items", headers=request_header)
        print(repr(user_info))
    elif menu == "Problem":
        pass