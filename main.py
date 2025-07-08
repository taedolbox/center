import streamlit as st

# 필요한 모든 앱 함수들을 임포트합니다.
from app.daily_worker_eligibility import daily_worker_eligibility_app
from app.early_reemployment import early_reemployment_app
from app.remote_assignment import remote_assignment_app
from app.wage_delay import wage_delay_app
from app.unemployment_recognition import unemployment_recognition_app

def main():
    st.set_page_config(
        page_title="실업급여 지원 시스템",
        page_icon="💼",
        layout="centered" # 페이지 내용을 중앙에 정렬
    )

    # 모든 CSS 스타일을 여기에 직접 삽입합니다. (이 부분은 변경 없음)
    st.markdown("""
    <style>
    /* 콤보박스 선택 영역 (현재 선택된 값 표시되는 부분) */
    div[data-baseweb="select"] > div:first-child {
        border: 2px solid #2196F3 !important; /* 기존 테두리 유지 */
        color: #2196F3 !important;            /* 텍스트 색상을 파란색으로 변경 */
        font-weight: 600 !important;
        background-color: #E3F2FD !important; /* 배경색을 밝은 파랑으로 변경 */
    }

    /* 콤보박스 내부 텍스트 (현재 선택된 값) */
    div[data-baseweb="select"] span {
        color: #2196F3 !important; /* 텍스트 색상을 파란색으로 변경 */
        font-weight: 600 !important;
    }

    /* 드롭다운 리스트 컨테이너 */
    div[data-baseweb="popover"] {
        z-index: 9999 !important; /* 다른 요소 위에 오도록 z-index 높임 */
        background-color: #FFFFFF !important; /* 드롭다운 배경색 하얀색으로 명확하게 */
        border: 1px solid #2196F3 !important; /* 테두리 추가 */
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important; /* 그림자 추가 */
    }

    /* 드롭다운 리스트 항목 */
    div[data-baseweb="select"] ul[role="listbox"] li {
        color: #2196F3 !important;
        font-weight: 600 !important;
        padding: 10px 15px !important; /* 패딩 조정 */
    }

    /* 드롭다운 리스트 항목 호버 시 */
    div[data-baseweb="select"] ul[role="listbox"] li:hover {
        background-color: #2196F3 !important;
        color: white !important;
    }

    /* 스크롤바 스타일링 (선택 사항, 깔끔하게 보이게) */
    div[data-baseweb="popover"]::-webkit-scrollbar {
        width: 8px;
    }
    div[data-baseweb="popover"]::-webkit-scrollbar-thumb {
        background-color: #bbdefb; /* 연한 파랑 */
        border-radius: 4px;
    }
    div[data-baseweb="popover"]::-webkit-scrollbar-track {
        background-color: #f1f1f1;
    }

    /* 다크 모드 스타일 */
    html[data-theme="dark"] div[data-baseweb="select"] > div:first-child {
        background-color: #31333F !important; /* 다크 모드 시 배경 */
        color: #FAFAFA !important; /* 다크 모드 시 텍스트 */
        border: 2px solid #4B4B4B !important;
    }
    html[data-theme="dark"] div[data-baseweb="select"] span {
        color: #FAFAFA !important; /* 다크 모드 시 텍스트 */
    }
    html[data-theme="dark"] div[data-baseweb="popover"] {
        background-color: #262730 !important;
        border: 1px solid #4B4B4B !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
    }
    html[data-theme="dark"] div[data-baseweb="select"] ul[role="listbox"] li {
        color: #FAFAFA !important;
    }
    html[data-theme="dark"] div[data-baseweb="select"] ul[role="listbox"] li:hover {
        background-color: #45475A !important;
        color: white !important;
    }

    /* 달력 그리드 */
    .calendar {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        width: 100%;
        background: #fff;
        padding: 10px;
        border-radius: 8px;
    }

    /* 요일 헤더 */
    .day-header {
        aspect-ratio: 1/1;
        display: flex;
        justify-content: center;
        align-items: center;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-size: 14px;
        font-weight: bold;
        color: #333;
    }
    .day-header.sunday {
        color: red;
    }
    .day-header.saturday {
        color: blue;
    }

    /* 날짜 */
    .day {
        aspect-ratio: 1/1;
        display: flex;
        justify-content: center;
        align-items: center;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-size: 16px;
        color: #333;
    }

    .day.sunday {
        color: red;
    }
    .day.saturday {
        color: blue;
    }

    /* 빈칸 */
    .day.empty {
        border: none;
        background: none;
    }
    </style>
    """, unsafe_allow_html=True)


    # 각 메뉴에 연결될 함수 매핑
    menu_functions = {
        "임금 체불 판단": wage_delay_app,
        "원거리 발령 판단": remote_assignment_app,
        "실업인정": unemployment_recognition_app,
        "조기재취업수당": early_reemployment_app,
        "실업급여 신청 가능 시점": lambda: st.info("이곳은 일반 실업급여 신청 가능 시점 안내 페이지입니다. 관련 기능이 구현되면 이곳에 표시됩니다."),
        "일용직(건설일용포함)": daily_worker_eligibility_app
    }

    # 메뉴와 표시될 제목을 한 곳에서 관리 (이 딕셔너리는 이제 고정된 제목을 위해 사용되지 않습니다.)
    menu_display_names = {
        "임금 체불 판단": "💸 임금 체불 판단",
        "원거리 발령 판단": "📍 원거리 발령 판단",
        "실업인정": "📄 실업인정",
        "조기재취업수당": "🏗️ 조기재취업수당 요건 판단",
        "실업급여 신청 가능 시점": "⏰ 실업급여 신청 가능 시점",
        "일용직(건설일용포함)": "🚧 일용직(건설일용포함) 실업급여"
    }

    # 모든 메뉴 목록 (순서 중요) - menu_display_names의 키를 사용하여 생성
    menus = ["메뉴 선택"] + list(menu_display_names.keys())

    # 1. 초기 메뉴 인덱스 결정 (URL 또는 세션 상태)
    menu_param_from_url = st.query_params.get("menu", None)

    if "current_menu_idx" not in st.session_state:
        if menu_param_from_url and menu_param_from_url.isdigit():
            parsed_menu_idx = int(menu_param_from_url) - 1
            if 0 <= parsed_menu_idx < len(menus):
                st.session_state.current_menu_idx = parsed_menu_idx
            else:
                st.session_state.current_menu_idx = 0
        else:
            st.session_state.current_menu_idx = 0

    # 2. st.selectbox에서 값 변경 시 세션 상태 및 URL 업데이트
    def on_menu_change():
        selected_menu_name = st.session_state.main_menu_select_key
        st.session_state.current_menu_idx = menus.index(selected_menu_name)

        if st.session_state.current_menu_idx == 0:
            if "menu" in st.query_params:
                del st.query_params["menu"] # "메뉴 선택" 시 URL 파라미터 제거
        else:
            # 선택된 메뉴의 인덱스를 1을 더하여 URL 파라미터로 저장 (사람에게 친숙한 1부터 시작)
            st.query_params["menu"] = str(st.session_state.current_menu_idx + 1)

    # 메인 화면에 메뉴 선택 콤보박스 배치
    st.selectbox(
        "📋 메뉴 선택",
        menus,
        index=st.session_state.current_menu_idx, # 현재 세션 상태의 인덱스 사용
        key="main_menu_select_key", # 콜백 함수를 위한 키
        on_change=on_menu_change # 값 변경 시 on_change 콜백 함수 호출
    )

    # --- 콤보박스와 아래 콘텐츠를 구분하는 시각적 구분선 추가 ---
    st.markdown("---")

    # ★ 변경된 부분: 이제 이 제목과 주의사항은 조건 없이 항상 표시됩니다. ★
    st.markdown(
        "<span style='font-size:22px; font-weight:600;'>🏗️ 조기재취업수당 요건 판단</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='font-size:18px; font-weight:700; margin-bottom:10px;'>ⓘ 실업급여 도우미는 참고용입니다. 실제 가능 여부는 고용센터 판단을 따릅니다.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---") # 공통 문구 아래 시각적 구분선 추가
    # --- 고정 문구 추가 종료 ---

    # 3. 세션 상태의 current_menu_idx에 따라 화면 출력
    selected_idx = st.session_state.current_menu_idx
    selected_menu_name = menus[selected_idx] # 현재 선택된 메뉴의 이름

    if selected_idx == 0:
        # "메뉴 선택" 시 보여줄 초기 화면 내용
        # 이제 위에 고정된 제목/주의사항 아래에 환영 메시지가 표시됩니다.
        st.markdown(
            """
            <div style="padding: 20px; border-radius: 10px; background-color: #f0f8ff; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #0d47a1; margin-bottom: 15px;">🌟 실업급여 지원 시스템에 오신 것을 환영합니다!</h3>
                <p style="font-size: 16px; line-height: 1.6; color: #333333;">  이 시스템은 <b>실업급여 수급 자격</b> 및 <b>조기재취업수당</b>과 관련된 정보를 쉽고 빠르게 확인하실 수 있도록 돕습니다.
                    <br><br>
                    궁금한 기능을 위에 있는 <b>'📋 메뉴 선택' 콤보박스에서 선택</b>해 주세요.
                </p>
                <ul style="font-size: 15px; line-height: 1.8; margin-top: 15px; color: #333333;">
                    <li>🔹 <b>임금 체불 판단:</b> 임금 체불로 인한 이직 사유 가능성을 판단합니다.</li>
                    <li>🔹 <b>원거리 발령 판단:</b> 원거리 발령으로 인한 이직 사유 가능성을 판단합니다.</li>
                    <li>🔹 <b>실업인정:</b> 실업인정 신청 및 관련된 정보를 확인합니다.</li>
                    <li>🔹 <b>조기재취업수당:</b> 조기재취업수당 신청 가능 여부를 판단합니다.</li>
                    <li>🔹 <b>실업급여 신청 가능 시점:</b> 일반 실업급여 신청 가능 시점을 안내합니다.</li>
                    <li>🔹 <b>일용직(건설일용포함):</b> 일용직 근로자의 실업급여 신청 가능 시점을 판단합니다.</li>
                </ul>
                <p style="font-size: 14px; color: #555; margin-top: 20px;">
                    💡 <b>주의:</b> 본 시스템의 결과는 참고용이며, 최종적인 실업급여 수급 여부는 관할 고용센터의 판단에 따릅니다.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown("---") # 또 다른 시각적 구분선
    else:
        # 선택된 메뉴에 해당하는 함수 호출 (menu_functions 딕셔너리 사용)
        if selected_menu_name in menu_functions:
            menu_functions[selected_menu_name]()
        else:
            st.error("선택된 메뉴에 해당하는 페이지를 찾을 수 없습니다.")
            st.info("다시 메뉴를 선택해주세요.")

if __name__ == "__main__":
    main()
