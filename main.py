import streamlit as st
from app.daily_worker_eligibility import daily_worker_eligibility_app
from app.early_reemployment import early_reemployment_app
from app.remote_assignment import remote_assignment_app
from app.wage_delay import wage_delay_app
from app.unemployment_recognition import unemployment_recognition_app
from app.questions import get_employment_questions, get_self_employment_questions, get_remote_assignment_questions, get_wage_delay_questions, get_daily_worker_eligibility_questions

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
            # ▼▼▼▼▼ 이 부분을 수정합니다! ▼▼▼▼▼
            "실업급여 신청가능 시점": ["실업급여 신청가능 시점", "일용직(건설일용포함)"] # '일용직' 하위 메뉴 추가 (이름 통일)
            # ▲▲▲▲▲ 이 부분을 수정합니다! ▲▲▲▲▲
        }
        all_questions = {
            "임금 체불 판단": get_wage_delay_questions(),
            "원거리 발령 판단": get_remote_assignment_questions(),
            "실업인정": [],
            "조기재취업수당": get_employment_questions() + get_self_employment_questions(),
            # ▼▼▼▼▼ 키 이름을 `menus`와 일치시키거나, 그대로 두려면 검색 쿼리에 영향이 갈 수 있음 ▼▼▼▼▼
            "일용직(건설일용포함)": get_daily_worker_eligibility_questions() # 'menus' 딕셔너리와 이름 통일을 권장
            # ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲ ▲▲▲▲▲
        }

        # ... (검색 및 메뉴 선택 로직은 그대로)

    st.markdown("---")

    # Call functions based on menu selection
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
    elif menu == "실업급여 신청가능 시점" and sub_menu:
        # ▼▼▼▼▼ 이 부분을 수정합니다! ▼▼▼▼▼
        #if sub_menu == "실업급여 신청가능 시점": # 메인 메뉴와 동일한 하위 메뉴
            # 여기에 해당 기능 (예: 일반 실업급여 신청 시점 로직)을 호출
            #st.info("이곳은 일반 실업급여 신청 가능 시점 안내 페이지입니다.")
        if sub_menu == "일용직(건설일용포함)": # 'menus'에서 사용한 이름과 정확히 일치
            daily_worker_eligibility_app()
        # ▲▲▲▲▲ 이 부분을 수정합니다! ▲▲▲▲▲

    # Auto-call function based on search query
    if search_query and selected_sub_menu:
        if selected_sub_menu == "임금 체불 판단":
            wage_delay_app()
        elif selected_sub_menu == "원거리 발령 판단":
            remote_assignment_app()
        elif selected_sub_menu == "실업인정":
            unemployment_recognition_app()
        elif selected_sub_menu == "조기재취업수당":
            early_reemployment_app()
        # ▼▼▼▼▼ 이 부분을 수정합니다! ▼▼▼▼▼
        elif selected_sub_menu == "실업급여 신청 가능 시점":
            #st.info("이곳은 일반 실업급여 신청 가능 시점 안내 페이지입니다.")
        elif selected_sub_menu == "일용직(건설일용포함)": # 'menus'에서 사용한 이름과 정확히 일치
            daily_worker_eligibility_app()
        # ▲▲▲▲▲ 이 부분을 수정합니다! ▲▲▲▲▲

    st.markdown("---")
    st.caption("ⓒ 2025 실업급여 도우미는 도움을 드리기 위한 목적입니다. 실제 가능 여부는 고용센터의 판단을 기준으로 합니다.")
    st.markdown("[나의 지역 고용센터 찾기](https://www.work24.go.kr/cm/c/d/0190/retrieveInstSrchLst.do)에서 자세한 정보를 확인하세요.")

if __name__ == "__main__":
    main()
    
