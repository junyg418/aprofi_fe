import streamlit as st
import json
import requests
from requests import Response
from code_editor import code_editor

API_URL = "http://210.115.227.15:8000"
# API_URL = "http://127.0.0.1:8000"

# st.set_option('client.showErrorDetails', True)
# st.set_option('client.toolbarMode', True)

def toggle_created_prob():
    st.session_state.created_prob = not st.session_state.created_prob

if "token" not in st.session_state:
    st.session_state.token = None
if "selected_option" not in st.session_state:
    st.session_state.selected_option = "all_problem"
if "problem_solve" not in st.session_state:
    st.session_state.problem_solve = False
if "submit" not in st.session_state:
    st.session_state["submit"] = None
if "test_cases" not in st.session_state:
    st.session_state.test_cases = [{"input": "", "output": ""} for _ in range(2)]
if "created_prob" not in st.session_state:
    st.session_state.created_prob = False

if "problem_id" not in st.query_params:
    st.query_params["problem_id"] = 0
if "token" not in st.query_params:
    st.query_params["token"] = ''
else:
    st.session_state.token = st.query_params["token"]

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

title, logout = st.columns([7, 2])
with title:
    st.title(f'Aprofi test')
st.markdown("---")
if st.session_state.token:
    if logout.button("logout"):
        st.session_state.token = None
        st.query_params["token"] = ''
        st.query_params["problem_id"] = 0
        st.rerun()
# --------------  세션 초기화  --------------
# --------------  풀이 페이지  --------------
if st.session_state.problem_solve:
    # -------- 풀이 설평 페이지 --------:
    if logout.button("Back to Problem"):
        st.session_state.problem_solve = False
        st.rerun()

    custom_btn = [
        {
            "name": "Copy",
            "hasText": True,
            "alwaysOn": True,
            "style": {"bottom": "0.44rem", "right": "0.4rem"}
        }, {
            "name": "Run",
            "feather": "Play",
            "primary": True,
            "hasText": True,
            "showWithIcon": True,
            "commands": ["submit"],
            "alwaysOn": True,
            "style": {"top": "0.46rem", "right": "0.4rem"}
        },
    ]
    mode_list = ["python", "c", "c++"]
    language = st.selectbox("lang:", mode_list, index=mode_list.index("python"))
    my_code = ''

    # -------- 문제 풀이 페이지 --------:
    if st.session_state.submit is None:
        response_dict = code_editor(my_code, lang=language if language == "python" else "c_cpp", focus=True,
                                    height="500px",
                                    buttons=custom_btn)

        if len(response_dict['id']) != 0 and (
                response_dict['type'] == "selection" or response_dict['type'] == "submit"):
            request_header = {
                "Authorization": f"Bearer {st.session_state.token}"
            }
            user_info = requests.get(f"{API_URL}/user/me/items", headers=request_header).json()
            solve_request_form = {
                "user_id": user_info["user_id"],
                "problem_id": st.query_params["problem_id"],
                "submitted_code": response_dict["text"],
                "code_language": language
            }
            st.session_state["submit"]: Response = requests.post(f"{API_URL}/api/solves", json=solve_request_form)
            st.rerun()
    else:
        if st.session_state.submit is not None:
            st.write(st.session_state["submit"].json())
            st.session_state.submit = None
        else:
            st.rerun()

# --------------  문제 페이지  --------------
elif int(st.query_params.problem_id):
    prob_name_lay, solve_lay = st.columns([8, 2])
    if logout.button("Back to List"):
        st.query_params.problem_id = 0
        st.rerun()
    if st.session_state.token:
        if solve_lay.button("**solve**"):
            st.session_state.problem_solve = True
            st.rerun()

    problem_id = st.query_params.problem_id
    problem_info: dict = requests.get(f"{API_URL}/api/problems/{problem_id}").json()
    prob_name_lay.title(f"{problem_info['name']}")
    st.write(f"{problem_info['description']}")
    with st.expander("**Input/Output Example**"):
        for testcase in json.loads(problem_info['testcase'])[:2]:  # 최대 2개만 표시
            st.markdown("---")
            st.markdown(f"**Input:**\n```\n{testcase['input']}\n```")
            st.markdown(f"**Output:**\n```\n{testcase['output']}\n```")

else:
    if not st.session_state.token:
        menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Problem"])
        if menu == "Login":
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
                    st.query_params["token"] = st.session_state.token
                    st.rerun()
                else:
                    st.error("failed")

        elif menu == "Register":
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
                    response = requests.post(f"{API_URL}/user/login", json=data)
                    if response.status_code == 200:
                        st.success("User Login successful")
                        st.session_state.token = response.json()["access_token"]
                        st.query_params["token"] = st.session_state.token
                        st.rerun()
                else:
                    st.error("failed")

        elif menu == "Problem":
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
                            <a href="?problem_id={problem['id']}&token={st.session_state.token}" target="_self">{problem['name']}</a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Login 상태
    if st.session_state.token:
        menu = st.sidebar.selectbox("Menu", ["Problem", "MyPage"])
        if menu == "MyPage":
            request_header = {
                "Authorization": f"Bearer {st.session_state.token}"
            }
            user_info = requests.get(f"{API_URL}/user/me/items", headers=request_header)
            user_info_data = user_info.json()
            st.text(f"ID    : {user_info_data['user_id']}")
            st.text(f"name  : {user_info_data['owner']}")
            st.text(f"email : {user_info_data['email']}")

        elif menu == "Problem":
            # -------- 문제 생성 페이지 --------
            logout.button("create problem" if not st.session_state.created_prob else "back to list",
                          on_click=toggle_created_prob)
            if st.session_state.created_prob:
                st.title("문제 제작")
                problem_title = st.text_input("제목")
                problem_description = st.text_area('문제 설명', height=500)
                for idx, case in enumerate(st.session_state.test_cases):
                    st.markdown("---")
                    st.write(f"**테스트 케이스 {idx + 1}**")
                    input_lay, output_lay = st.columns([5, 5])
                    case["input"] = input_lay.text_input(f"Input {idx + 1}", value=case["input"], key=f"input_{idx}")
                    case["output"] = output_lay.text_input(f"Output {idx + 1}", value=case["output"], key=f"output_{idx}")

                append_lay, submit_lay = st.columns([6, 1])
                if append_lay.button("+ 추가"):
                    st.session_state.test_cases.append({"input": "", "output": ""})

                if submit_lay.button("submit"):
                    request_json = {
                        "name": problem_title,
                        "description": problem_description,
                        "testcase": st.session_state.test_cases
                    }
                    requests.post(f"{API_URL}/api/problems", json=request_json)
                    # 초기화
                    st.session_state.test_cases = [{"input": "", "output": ""} for _ in range(2)]
                    st.session_state.created_prob = False
                    st.rerun()

            # --------   문제 리스트   --------
            else:
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
                                <a href="?problem_id={problem['id']}&token={st.session_state.token}" target="_self">{problem['name']}</a>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
