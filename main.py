import streamlit as st

from app.daily_worker_eligibility import daily_worker_eligibility_app
from app.early_reemployment import early_reemployment_app
from app.remote_assignment import remote_assignment_app
from app.wage_delay import wage_delay_app
from app.unemployment_recognition import unemployment_recognition_app
from app.questions import (
    get_employment_questions,
    get_self_employment_questions,
    get_remote_assignment_questions,
    get_wage_delay_questions,
    get_daily_worker_eligibility_questions
)

def update_selected_menu(filtered_menus, all_menus):
    selected_menu = st.session_state.menu_selector
    if selected_menu in filtered_menus:
        st.session_state.selected_menu = selected_menu
        menu_id = all_menus.index(selected_menu) + 1
        st.query_params["menu"] = str(menu_id)

def main():
    st.set_page_config(
        page_title="실업급여 지원 시스템",
        page_icon="💼",
        layout="centered"
    )

    # CSS 적용
    with open("static/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    all_menus = [
        "임금 체불 판단",
        "원거리 발령 판단",
        "실업인정",
        "조기재취업수당",
        "실업급여 신청 가능 시점",
        "일용직(건설일용포함)"
    ]

    menu_functions = {
        "임금 체불 판단": wage_delay_app,
        "원거리 발령 판단": remote_assignment_app,
        "실업인정": unemployment_recognition_app,
        "조기재취업수당": early_reemployment_app,
        "실업급여 신청 가능 시점": lambda: st.info("이곳은 일반 실업급여 신청 가능 시점 안내 페이지입니다."),
        "일용직(건설일용포함)": daily_worker_eligibility_app
    }

    all_questions = {
        "임금 체불 판단": get_wage_delay_questions(),
        "원거리 발령 판단": get_remote_assignment_questions(),
        "실업인정": [],
        "조기재취업수당": get_employment_questions() + get_self_employment_questions(),
        "실업급여 신청 가능 시점": [],
        "일용직(건설일용포함)": get_daily_worker_eligibility_questions()
    }

    with st.sidebar:
        st.markdown("### 🔍 검색")
        search_query = st.text_input("메뉴 또는 질문을 검색하세요", key="search_query")

        filtered_menus = all_menus
        if search_query:
            search_query = search_query.lower()
            filtered_menus = [
                menu for menu in all_menus
                if search_query in menu.lower() or
                any(search_query in q.lower() for q in all_questions.get(menu, []))
            ]

        # 세션 초기화
        if "selected_menu" not in st.session_state:
            query_params = st.query_params
            url_menu_id = query_params.get("menu", [None])[0]
            default_menu = None
            if url_menu_id:
                try:
                    menu_idx = int(url_menu_id) - 1
                    if 0 <= menu_idx < len(all_menus):
                        default_menu = all_menus[menu_idx]
                except ValueError:
                    pass
            st.session_state.selected_menu = default_menu if default_menu in all_menus else filtered_menus[0] if filtered_menus else None

        if filtered_menus:
            selected_menu = st.radio(
                "📋 메뉴",
                filtered_menus,
                index=filtered_menus.index(st.session_state.selected_menu)
                if st.session_state.selected_menu in filtered_menus else 0,
                key="menu_selector",
                on_change=lambda: update_selected_menu(filtered_menus, all_menus)
            )
            if selected_menu != st.session_state.selected_menu:
                st.session_state.selected_menu = selected_menu
                menu_id = all_menus.index(selected_menu) + 1
                st.query_params["menu"] = str(menu_id)
        else:
            st.warning("검색 결과에 해당하는 메뉴가 없습니다.")
            st.session_state.selected_menu = None

        st.markdown("---")
        st.markdown("[📌 고용센터 찾기](https://www.work24.go.kr/cm/c/d/0190/retrieveInstSrchLst.do)")

    st.markdown("---")

    if st.session_state.selected_menu:
        menu_functions.get(
            st.session_state.selected_menu,
            lambda: st.info("메뉴를 선택하세요.")
        )()
    else:
        st.info("왼쪽 사이드바에서 메뉴를 선택하거나 검색어를 입력하세요.")

if __name__ == "__main__":
    main()
