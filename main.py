import streamlit as st
from app.daily_worker_eligibility import daily_worker_eligibility_app
from app.early_reemployment import early_reemployment_app
from app.remote_assignment import remote_assignment_app
from app.wage_delay import wage_delay_app
from app.unemployment_recognition import unemployment_recognition_app
from app.questions import \
    get_employment_questions, \
    get_self_employment_questions, \
    get_remote_assignment_questions, \
    get_wage_delay_questions, \
    get_daily_worker_eligibility_questions # 이 부분은 이미 추가하셨으리라 가정합니다.

def main():
    st.set_page_config(page_title="실업급여 지원 시스템", page_icon="💼", layout="centered")

    # Apply custom CSS
    with open("static/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title("💼 실업급여 도우미")

    # Sidebar search functionality
    with st.sidebar:
        st.markdown("### 🔍 검색")
        search_query = st.text_input("메뉴 또는 질문을 검색하세요", key="search_query")

        # Menu and question definitions
        menus = {
            "수급자격": ["임금 체불 판단", "원거리 발령 판단"],
            "실업인정": ["실업인정"],
            "취업촉진수당": ["조기재취업수당"],
            # ▼▼▼▼▼ 여기가 핵심 수정! ▼▼▼▼▼
            "실업급여 신청가능 시점": ["실업급여 신청 가능 시점", "일용직(건설일용포함)"]
            # ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲
        }
        all_questions = {
            "임금 체불 판단": get_wage_delay_questions(),
            "원거리 발령 판단": get_remote_assignment_questions(),
            "실업인정": [],
            "조기재취업수당": get_employment_questions() + get_self_employment_questions(),
            "일용직(건설일용포함)": get_daily_worker_eligibility_questions()
        }

        # Filter menus based on search query
        filtered_menus = {}
        selected_sub_menu = None # 검색 결과로 선택된 하위 메뉴를 저장할 변수
        if search_query:
            search_query = search_query.lower()
            for main_menu, sub_menus in menus.items():
                filtered_sub_menus = [
                    sub for sub in sub_menus
                    if search_query in sub.lower() or
                    any(search_query in q.lower() for q in all_questions.get(sub, []))
                ]
                if filtered_sub_menus or search_query in main_menu.lower():
                    filtered_menus[main_menu] = filtered_sub_menus
                # 검색 결과로 선택된 하위 메뉴가 있을 경우 selected_sub_menu 업데이트
                for sub in sub_menus:
                    if search_query in sub.lower() or any(search_query in q.lower() for q in all_questions.get(sub, [])):
                        selected_sub_menu = sub
                        st.session_state.selected_menu = main_menu # 이 부분은 사이드바에서 메뉴 선택 시 사용될 수 있음
                        break
                if selected_sub_menu:
                    break # 하위 메뉴가 검색으로 선택되었으면 더 이상 검색하지 않음
        else:
            filtered_menus = menus

        # Main menu selection
        # ▼▼▼▼▼ 여기도 수정: 초기값을 None으로 설정하여 NameError 방지 ▼▼▼▼▼
        menu = None
        sub_menu = None

        if filtered_menus:
            menu = st.selectbox("📌 메뉴를 선택하세요", list(filtered_menus.keys()), key="main_menu")
            if filtered_menus.get(menu): # .get()을 사용하여 키가 없을 때 오류 방지
                sub_menu = st.radio("📋 하위 메뉴", filtered_menus[menu], key="sub_menu")
            else:
                st.warning("검색 결과에 해당하는 하위 메뉴가 없습니다.")
        else:
            st.warning("검색 결과에 해당하는 메뉴가 없습니다.")
        # ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲

    st.markdown("---")

    # Call functions based on menu selection
    # ▼▼▼▼▼ 가장 중요한 NameError 방지 조건 추가 ▼▼▼▼▼
    if menu is not None and sub_menu is not None:
        if menu == "수급자격" and sub_menu:
            if sub_menu == "임금 체불 판단":
                wage_delay_app()
            elif sub_menu == "원거리 발령 판단":
                remote_assignment_app()
        elif menu == "실업인정" and sub_menu:
            if sub_menu == "실업인정":
                unemployment_recognition_app()
        elif menu == "취업촉진수당" and sub_menu:
            if sub_menu == "조기재취업수당":
                early_reemployment_app()
        # ▼▼▼▼▼ 여기가 핵심 수정! ▼▼▼▼▼
        elif menu == "실업급여 신청가능 시점" and sub_menu:
            if sub_menu == "실업급여 신청 가능 시점":
                # 여기에 일반 실업급여 신청 시점 안내 로직을 추가
                st.info("이곳은 일반 실업급여 신청 가능 시점 안내 페이지입니다. 자세한 내용은 고용센터에 문의하세요.")
            elif sub_menu == "일용직(건설일용포함)":
                  daily_worker_eligibility_app()
        # ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲
    else:
        st.info("왼쪽 사이드바에서 메뉴를 선택하거나 검색어를 입력하여 원하는 정보를 찾아보세요.")


    # Auto-call function based on search query
    # ▼▼▼▼▼ 여기도 NameError 방지 조건 추가 ▼▼▼▼▼
    if search_query and selected_sub_menu is not None:
        if selected_sub_menu == "임금 체불 판단":
            wage_delay_app()
        elif selected_sub_menu == "원거리 발령 판단":
            remote_assignment_app()
        elif selected_sub_menu == "실업인정":
            unemployment_recognition_app()
        elif selected_sub_menu == "조기재취업수당":
            early_reemployment_app()
        elif selected_sub_menu == "일용직(건설일용포함)":
            daily_worker_eligibility_app()    
        # ▼▼▼▼▼ 여기가 핵심 수정! ▼▼▼▼▼
    #    elif selected_sub_menu == "실업급여 신청 가능 시점":
    #        st.info("이곳은 일반 실업급여 신청 가능 시점 안내 페이지입니다. 자세한 내용은 고용센터에 문의하세요.")

    st.markdown("---")
    st.caption("ⓒ 2025 실업급여 도우미는 도움을 드리기 위한 목적입니다. 실제 가능 여부는 고용센터의 판단을 기준으로 합니다.")
    st.markdown("[나의 지역 고용센터 찾기](https://www.work24.go.kr/cm/c/d/0190/retrieveInstSrchLst.do)에서 자세한 정보를 확인하세요.")

if __name__ == "__main__":
    main()
