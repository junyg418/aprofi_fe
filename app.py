import streamlit as st
import json
import requests

API_URL = "http://210.115.227.15:8000"
if "token" not in st.session_state:
    st.session_state.token = None
if "selected_option" not in st.session_state:
    st.session_state.selected_option = "all_problem"
if "problem_id" not in st.query_params:
    st.query_params["problem_id"] = 0

st.markdown(
    """
    <style>
    .selected-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        margin: 5px;
    }
    .unselected-button {
        background-color: #f1f1f1;
        color: black;
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        margin: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if int(st.query_params.problem_id):
    if st.button("Back to Problem List"):
        st.query_params.problem_id = 0
        st.rerun()
    problem_id = st.query_params.problem_id
    problem_info: dict = requests.get(f"{API_URL}/api/problems/{problem_id}").json()
    st.title(f"{problem_info['name']}")
    st.write(f"{problem_info['description']}")
    with st.expander("Input/Output Example"):
        for testcase in json.loads(problem_info['testcase'])[:2]:  # 최대 2개만 표시
            st.markdown("---")
            st.markdown(f"**Input:**\n```\n{testcase['input']}\n```")
            st.markdown(f"**Output:**\n```\n{testcase['output']}\n```")

else:
    st.title('Aprofi test')

    if st.session_state.token is None:
        menu = st.sidebar.selectbox("Menu", ["Register", "Login", "Problem"])
        if menu == "Register":
            st.subheader("Register")
            username = st.text_input("username")
            email = st.text_input("email")
            user_id = st.text_input("user_id")
            password = st.text_input("password", type="password")
            password_check = st.text_input("password_ch", type="password")

            if password == password_check and st.button("submit"):
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
                    st.rerun()
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
            user_info_data = user_info.json()[0]
            st.text(f"ID    : {user_info_data['user_id']}")
            st.text(f"name  : {user_info_data['owner']}")
            st.text(f"email : {user_info_data['email']}")

        elif menu == "Problem":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("my_problem"):
                    st.session_state.selected_option = "my_problem"
            with col2:
                if st.button("all_problem"):
                    st.session_state.selected_option = "all_problem"

            problems = None
            if st.session_state.selected_option == "my_problem":
                problems = requests.get(f"{API_URL}/api/problems").json()
            elif st.session_state.selected_option == "all_problem":
                problems = requests.get(f"{API_URL}/api/problems").json()

            for problem in problems:
                st.markdown(
                    """
                    <style>
                    .problem-row {
                        display: flex;
                        justify-content: flex-start;
                        align-items: center;
                        padding: 5px 0;
                    }
                    .problem-id {
                        width: 100px;  /* 고정 너비 */
                        text-align: center;
                        font-weight: bold;
                    }
                    .problem-name {
                        flex-grow: 1;  /* 남은 공간을 차지 */
                        font-weight: bold;
                    }
                    .problem-name a {
                        text-decoration: none;
                        color: inherit;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div class="problem-row">
                        <div class="problem-id">{problem['id']}</div>
                        <div class="problem-name">
                            <a href="?problem_id={problem['id']}" target="_self">{problem['name']}</a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )