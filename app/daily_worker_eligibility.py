import streamlit as st
import pandas as pd
from app.questions import get_daily_worker_eligibility_questions
from datetime import datetime, timedelta, date
import calendar

# 달력의 시작 요일을 일요일로 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜와 시간을 기반으로 KST 오후 XX:XX 형식을 생성
current_datetime = datetime.now()
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')

def get_date_range(apply_date):
    """
    신청일을 기준으로 이전 달 초일부터 신청일까지의 날짜 범위를 반환합니다.
    반환되는 날짜들은 datetime.date 객체들의 리스트입니다.
    """
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    """
    달력을 렌더링하고 HTML/CSS/JS를 이용한 날짜 선택 기능을 제공합니다.
    선택된 날짜, 현재 날짜, 신청일 이후 날짜는 표시하지 않습니다.
    """
    # 초기 세션 상태 설정
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now().date()

    # 달력 표시할 월 범위 계산 (apply_date까지 표시)
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    # 사용자 정의 CSS 주입
    st.markdown(f"""
    <style>
    /* Streamlit 기본 버튼 스타일 오버라이딩 */
    button[data-testid="stButton"] {{
        width: 100% !important; /* 부모 div 너비 100% 사용 */
        height: 100% !important; /* 부모 div 높이 100% 사용 */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important; /* 기본 버튼 테두리 제거 */
        background: none !important; /* 기본 버튼 배경 제거 */
        color: inherit !important; /* 부모 폰트 색상 상속 */
        font-size: 1em !important; /* 기본 폰트 크기 사용 */
        cursor: pointer !important;
        transition: none !important; /* 버튼 호버/클릭 전환 효과 제거 */
        box-shadow: none !important; /* 기본 버튼 그림자 제거 */
    }}

    /* Streamlit 내부 버튼 텍스트의 폰트 사이즈 조정 */
    button[data-testid="stButton"] p {{
        font-size: 1.1em !important; /* 날짜 숫자 폰트 크기 (calendar-day-box와 유사하게) */
        margin: 0 !important; /* 마크다운 p 태그 마진 제거 */
    }}

    /* 전체 폰트 Streamlit 기본 폰트 사용 */

    /* 달력 전체 컨테이너 가운데 정렬을 위한 상위 요소에 Flexbox 적용 */
    /* Streamlit이 컬럼을 감싸는 div의 data-testid을 확인하여 적절히 선택 */
    /* st.columns가 생성하는 가장 바깥 div를 찾아 중앙 정렬 */
    div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stHorizontalBlock"] {{
        display: flex;
        flex-direction: column; /* 세로 방향으로 정렬 (월별 헤더, 요일 헤더, 달력 그리드) */
        align-items: center; /* 수평 가운데 정렬 */
        width: 100%; /* 부모 너비 채우기 */
    }}


    /* 월별 헤더 스타일 */
    div[data-testid="stMarkdownContainer"] h3 {{
        background-color: #f0f0f0 !important; /* 라이트 모드 */
        color: #000000 !important; /* 라이트 모드 */
        text-align: center; /* 월별 헤더 가운데 정렬 */
        padding: 8px 0; /* 패딩 증가 */
        margin-bottom: 15px; /* 아래 여백 증가 */
        font-size: 1.5em !important; /* 월별 헤더 폰트 크기 증가 */
        width: 100%; /* 월별 헤더 너비 100% */
    }}

    /* Light Mode */
    /* 요일 헤더 기본 글자색 (라이트 모드) */
    .day-header span {{
        color: #000000 !important; /* 라이트 모드일 때 검정색 */
    }}

    /* Dark Mode (prefers-color-scheme) */
    @media (prefers-color-scheme: dark) {{
        div[data-testid="stMarkdownContainer"] h3 {{
            background-color: #2e2e2e !important; /* 다크 모드 */
            color: #ffffff !important; /* 다크 모드 */
        }}
        /* 요일 헤더 기본 글자색 (다크 모드) */
        .day-header span {{
            color: #ffffff !important; /* 다크 모드일 때 흰색 */
        }}
    }}

    /* 요일 헤더 공통 스타일 (폰트 크기 및 정렬) */
    .day-header span {{
        font-size: 1.1em !important; /* 요일 폰트 크기 */
        text-align: center !important; /* 가운데 정렬 */
        display: block !important; /* text-align을 위해 block으로 설정 */
        width: 100% !important; /* 부모 div의 너비에 맞춤 */
        font-weight: bold; /* 요일 글자 두껍게 */
        padding: 5px 0; /* 요일 패딩 추가 */
    }}

    /* 요일 헤더 특정 요일 색상 (라이트/다크 모드 공통) */
    /* 일요일 빨간색 */
    .day-header:nth-child(1) span {{
        color: red !important;
    }}
    /* 토요일 파란색 */
    .day-header:nth-child(7) span {{
        color: blue !important;
    }}

    /* 커스텀 날짜 박스 스타일 (버튼처럼 동작) */
    .calendar-day-box {{
        width: 100%; /* 부모 컬럼의 100%를 사용 */
        height: 5vw; /* 뷰포트 너비에 비례하여 높이 설정 */
        max-height: 50px; /* 너무 커지지 않도록 최대 높이 설정 */
        min-height: 38px; /* 너무 작아지지 않도록 최소 높이 설정 (모바일 기준) */
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        margin: 0; /* st.columns의 gap을 사용할 것이므로 margin은 0 */
        border: 1px solid #ddd; /* 기본 테두리색 (라이트 모드) */
        background-color: #ffffff; /* 기본 배경색 (라이트 모드) */
        cursor: pointer;
        transition: all 0.1s ease; /* 부드러운 전환 효과 */
        border-radius: 5px; /* 약간 둥근 모서리 */
        font-size: 1.1em; /* 날짜 숫자 폰트 크기 증가 */
        color: #000000; /* 날짜 숫자 글자색 (라이트 모드) */
        box-sizing: border-box; /* 패딩, 보더가 너비 계산에 포함되도록 */
        user-select: none; /* 텍스트 선택 방지 */
    }}
    /* Dark Mode 날짜 박스 */
    @media (prefers-color-scheme: dark) {{
        .calendar-day-box {{
            border: 1px solid #444; /* 다크 모드 테두리색 */
            background-color: #1e1e1e; /* 다크 모드 배경색 */
            color: #ffffff; /* 날짜 숫자 글자색 (다크 모드) */
        }}
    }}

    /* 호버 시 효과 */
    .calendar-day-box:hover {{
        background-color: #e0e0e0; /* 호버 시 밝은 회색 (라이트 모드) */
        border-color: #bbb;
    }}
    @media (prefers-color-scheme: dark) {{
        .calendar-day-box:hover {{
            background-color: #2a2a2a; /* 호버 시 어두운 회색 (다크 모드) */
            border-color: #666;
        }}
    }}

    /* 오늘 날짜 스타일 (선택되지 않았을 때만 적용) */
    .calendar-day-box.current-day:not(.selected-day) {{
        border: 2px solid blue !important; /* 오늘 날짜 파란색 테두리 */
    }}

    /* 선택된 날짜 스타일 */
    .calendar-day-box.selected-day {{
        background-color: rgba(255, 0, 0, 0.4) !important; /* 빨간색 40% 투명도 */
        color: #ffffff !important; /* 흰색 글씨 */
        border: 1px solid rgba(255, 0, 0, 0.4) !important; /* 선택된 날짜 테두리 */
    }}

    /* Streamlit st.columns가 생성하는 각 열에 대한 스타일 */
    /* 요일 헤더를 감싸는 stHorizontalBlock */
    div[data-testid="stHorizontalBlock"] > div:first-child {{ /* 첫 번째 stHorizontalBlock (요일 헤더) */
        max-width: 400px; /* 달력 전체의 최대 너비 (조절 가능) */
        margin: 0 auto; /* 중앙 정렬 */
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 2px; /* 열 사이의 간격 */
    }}

    /* 달력 날짜 그리드를 감싸는 stHorizontalBlock */
    div[data-testid="stHorizontalBlock"] > div:nth-child(n+2) {{ /* 두 번째 이후 stHorizontalBlock (날짜 그리드) */
        max-width: 400px; /* 달력 전체의 최대 너비 (조절 가능) */
        margin: 0 auto 10px auto; /* 중앙 정렬, 아래 여백 추가 */
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 2px; /* 날짜 박스 사이의 간격 */
    }}

    /* 각 열 (요일/날짜) */
    div[data-testid="stHorizontalBlock"] > div > div {{
        flex-grow: 0; /* 늘어나지 않음 */
        flex-shrink: 0; /* 줄어들지 않음 */
        flex-basis: calc(100% / 7 - 2px); /* 7개 열이 대략적으로 균등하게, gap 고려 */
        /* min-width는 calendar-day-box에서 제어하므로 여기서는 0으로 */
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        box-sizing: border-box; /* 패딩, 보더가 너비 계산에 포함되도록 */
        display: flex; /* 내부 요소 정렬을 위해 flexbox 사용 */
        justify-content: center; /* 박스 가운데 정렬 */
        align-items: center; /* 박스 세로 가운데 정렬 */
    }}

    /* 모바일 반응형 조절 */
    @media (max-width: 600px) {{
        div[data-testid="stHorizontalBlock"] > div {{
            max-width: 100%; /* 모바일에서는 너비 100% */
        }}
        div[data-testid="stHorizontalBlock"] > div > div {{
            flex-basis: calc(100% / 7 - 2px); /* 모바일에서는 간격 약간 줄여서 7개 열 맞춤 */
        }}
        .calendar-day-box {{
            height: 8vw; /* 모바일에서 높이 조절 */
            max-height: 45px; /* 모바일에서 최대 높이 */
            min-height: 30px; /* 모바일에서 최소 높이 */
            font-size: 0.9em;
        }}
        button[data-testid="stButton"] p {{
            font-size: 0.9em !important; /* 모바일 폰트 크기 */
        }}
        .day-header span {{
            font-size: 0.8em !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # 각 월별 달력 렌더링
    for year, month in months_to_display:
        st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

        # 요일 헤더 생성 (st.columns 사용)
        cols = st.columns(7, gap="small") # gap="small"로 컬럼 자체의 간격 유지
        for i, day_name in enumerate(days_of_week_korean):
            with cols[i]:
                st.markdown(f'<div class="day-header"><span><strong>{day_name}</strong></span></div>', unsafe_allow_html=True)

        # 달력 날짜 박스 생성 (apply_date 이후 날짜 제외)
        for week in cal:
            cols = st.columns(7, gap="small") # gap="small"로 컬럼 자체의 간격 유지
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.empty() # 빈 칸을 위한 Streamlit empty
                    else:
                        date_obj = date(year, month, day)
                        # 신청일 이후 날짜는 표시하지 않음 (빈 칸)
                        if date_obj > apply_date:
                            st.empty()
                            continue

                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date

                        # 버튼 클릭 시 동작할 콜백 함수 정의
                        def _on_date_click(clicked_date_obj):
                            if clicked_date_obj in st.session_state.selected_dates:
                                st.session_state.selected_dates.discard(clicked_date_obj)
                            else:
                                st.session_state.selected_dates.add(clicked_date_obj)

                        # 날짜 텍스트 (오늘 날짜는 굵게)
                        display_day_text = str(day)
                        # CSS 클래스 적용을 위해 div로 감싸고, 여기에 버튼을 넣는 구조
                        # st.button은 자체적으로 `data-testid="stButton"`을 가짐
                        # 이 버튼을 `.calendar-day-box` 스타일로 강제 오버라이딩 할 것임
                        st.markdown(
                            f"""
                            <div class="calendar-day-box {'selected-day' if is_selected else ''} {'current-day' if is_current else ''}"
                                data-date="{date_obj.strftime('%Y-%m-%d')}"
                            >
                                <button type="button" class="st-emotion-cache-YOUR_BUTTON_CLASS_HERE"
                                    onclick="
                                        var dateStr = '{date_obj.strftime('%Y-%m-%d')}';
                                        var input = parent.document.getElementById('hidden_date_input_for_js');
                                        if (input) {{
                                            input.value = dateStr;
                                            input.dispatchEvent(new Event('change'));
                                        }}
                                    ">
                                    {display_day_text}
                                </button>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        # 클릭 이벤트를 받기 위한 숨겨진 text_input을 다시 사용합니다.
                        # `st.button`을 직접 사용하는 것보다, HTML/JS를 통해 Streamlit 상태를 조작하는 것이
                        # 달력 같은 복잡한 레이아웃에 더 유연합니다.
                        # `st.button`의 콜백은 전체 앱을 재실행시키므로, 많은 버튼 클릭 시 성능 저하가 있을 수 있습니다.
                        # 숨겨진 text_input을 통한 방식은 변경이 감지될 때만 재실행되므로 더 효율적일 수 있습니다.

    # JavaScript에서 클릭된 날짜를 받아올 숨겨진 st.text_input
    # 이 인풋의 `on_change` 콜백에서 `st.session_state.selected_dates`를 업데이트합니다.
    # value는 st.text_input의 현재 값을 나타냅니다.
    # 초기화 시 빈 문자열로 설정하여 불필요한 재트리거 방지
    # key가 변경될 때마다 새로운 위젯으로 인식되므로, key는 고정합니다.
    st.text_input("Hidden input for date click", key="hidden_date_input_for_js", value="",
                    on_change=lambda: _update_selected_dates_from_js(st.session_state.hidden_date_input_for_js))

    # JavaScript에서 전달받은 날짜를 파이썬 상태로 업데이트하는 콜백 함수
    def _update_selected_dates_from_js(date_str):
        if date_str:
            clicked_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            if clicked_date_obj in st.session_state.selected_dates:
                st.session_state.selected_dates.discard(clicked_date_obj)
            else:
                st.session_state.selected_dates.add(clicked_date_obj)
            st.session_state.hidden_date_input_for_js = "" # 처리 후 입력 값 초기화

    # 현재 선택된 근무일자 목록 표시
    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    return st.session_state.selected_dates

def daily_worker_eligibility_app():
    """
    일용근로자 수급자격 요건 모의계산 앱의 메인 함수입니다.
    """
    st.header("일용근로자 수급자격 요건 모의계산")

    # 현재 날짜와 시간 표시
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    # 요건 조건 설명
    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    # 수급자격 신청일 선택 (자유롭게 선택 가능)
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.now().date(), key="apply_date_input")

    # 날짜 범위 및 시작일 가져오기
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_days = render_calendar_interactive(apply_date) # 함수 호출 변경
    st.markdown("---")

    # 조건 1 계산 및 표시
    total_days = len(date_range_objects)
    worked_days = len(selected_days)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    if condition1:
        st.success("✅ 조건 1 충족: 근무일 수가 기준 미만입니다.")
    else:
        st.warning("❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.")

    # 조건 2 계산 및 표시 (건설일용근로자 기준)
    condition2 = False
    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_days for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    if no_work_14_days:
        st.success(f"✅ 조건 2 충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 없습니다.")
    else:
        st.warning(f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재합니다.")

    st.markdown("---")

    # 조건 1 불충족 시 미래 신청일 제안
    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        found_suggestion = False
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_days if d <= future_date)

            if worked_days_future < threshold_future:
                st.info(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후에 신청하면 요건을 충족할 수 있습니다.")
                found_suggestion = True
                break
        if not found_suggestion:
            st.warning("❗앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.")

    # 조건 2 불충족 시 미래 신청일 제안 (건설일용근로자 기준)
    if not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        last_worked_day = max((d for d in selected_days if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")

    st.subheader("📌 최종 판단")
    # 일반일용근로자: 조건 1만 판단
    if condition1:
        st.success(f"✅ 일반일용근로자: 신청 가능\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
    else:
        st.error(f"❌ 일반일용근로자: 신청 불가능\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.**")

    # 건설일용근로자: 조건 1과 조건 2 모두 판단
    if condition1 and condition2:
        st.success(f"✅ 건설일용근로자: 신청 가능\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
    else:
        error_message = "❌ 건설일용근로자: 신청 불가능\n\n"
        if not condition1:
            error_message += f"**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.**\n\n"
        if not condition2:
            error_message += f"**신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 있습니다.**"
        st.error(error_message)

if __name__ == "__main__":
    daily_worker_eligibility_app()
