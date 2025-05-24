import streamlit as st
import pandas as pd
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
    달력을 렌더링하고 버튼 클릭으로 날짜 선택 기능을 제공합니다.
    선택된 날짜에 원형 배경을 표시합니다.
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
    /* 컬럼 간격 조절 (7열) */
    div[data-testid="stHorizontalBlock"] > div {
        flex-grow: 0;
        flex-shrink: 0;
        flex-basis: calc(100% / 7 + 5px);
        min-width: 45px;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2px;
        margin: 0 2px;
    }

    /* 요일 헤더와 날짜 간격 분리 */
    .day-header-container {
        margin-bottom: 10px;
    }

    /* 기본 날짜 스타일 */
    .calendar-day-box {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 1px solid #ddd;
        background-color: #ffffff;
        color: #000000;
        text-align: center;
        line-height: 32px;
        margin: auto;
        cursor: pointer;
        transition: all 0.1s ease;
    }
    @media (prefers-color-scheme: dark) {
        .calendar-day-box {
            border: 1px solid #444;
            background-color: #1e1e1e;
            color: #ffffff;
        }
    }

    /* 호버 시 효과 */
    .calendar-day-box:hover {
        background-color: #e0e0e0;
        border-color: #bbb;
    }
    @media (prefers-color-scheme: dark) {
        .calendar-day-box:hover {
            background-color: #2a2a2a;
            border-color: #666;
        }
    }

    /* 오늘 날짜 스타일 (선택되지 않았을 때) */
    .calendar-day-box.current-day:not(.selected-day) {
        border: 2px solid #00aaff;
    }

    /* 선택된 날짜 스타일 (원형 배경) */
    .calendar-day-box.selected-day {
        background-color: #4CAF50;
        color: #ffffff;
        border: 2px solid #4CAF50;
        font-weight: bold;
    }

    /* 비활성화된 날짜 */
    .disabled-day {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 1px solid #555;
        background-color: #2e2e2e;
        color: #666;
        text-align: center;
        line-height: 32px;
        margin: auto;
    }

    /* 빈 날짜 */
    .empty-day {
        width: 32px;
        height: 32px;
        margin: auto;
    }

    /* 요일 헤더 스타일 */
    .day-header span {
        font-size: 1.1em;
        text-align: center;
        display: block;
        width: 100%;
        font-weight: bold;
        padding: 5px 0;
        color: #000000;
    }
    @media (prefers-color-scheme: dark) {
        .day-header span {
            color: #ffffff;
        }
    }
    .day-header:nth-child(1) span { color: red; }
    .day-header:nth-child(7) span { color: blue; }

    /* 월 헤더 스타일 */
    h3 {
        background-color: #f0f0f0;
        color: #000000;
        text-align: center;
        padding: 8px 0;
        margin-bottom: 15px;
        font-size: 1.5em;
        width: 100%;
    }
    @media (prefers-color-scheme: dark) {
        h3 {
            background-color: #2e2e2e;
            color: #ffffff;
        }
    }

    /* 모바일 반응형 */
    @media (max-width: 600px) {
        .calendar-day-box {
            height: 8vw;
            max-height: 45px;
            min-height: 30px;
            font-size: 0.9em;
        }
        .day-header span {
            font-size: 0.8em;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # 각 월별 달력 렌더링
    for year, month in months_to_display:
        st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)

        # 요일 헤더 (일~토) 컨테이너로 분리
        st.markdown('<div class="day-header-container">', unsafe_allow_html=True)
        cols = st.columns(7)
        weekdays = ["일", "월", "화", "수", "목", "금", "토"]
        for i, day_name in enumerate(weekdays):
            with cols[i]:
                st.markdown(f'<div class="day-header"><span>{day_name}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 달력 날짜 박스 생성
        cal = calendar.monthcalendar(year, month)
        for week_idx, week in enumerate(cal):
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.markdown('<div class="empty-day"></div>', unsafe_allow_html=True)
                    else:
                        date_obj = date(year, month, day)
                        if date_obj > apply_date:
                            st.markdown('<div class="disabled-day"></div>', unsafe_allow_html=True)
                            continue

                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date
                        is_disabled = date_obj > apply_date

                        # 버튼으로 클릭 이벤트 처리
                        button_key = f"date_{date_obj.isoformat()}_week_{week_idx}"
                        if st.button(str(day), key=button_key, disabled=is_disabled):
                            toggle_date(date_obj)

                        # 선택 상태에 따라 스타일링
                        class_name = "calendar-day-box"
                        if is_selected:
                            class_name += " selected-day"
                        elif is_current:
                            class_name += " current-day"
                        st.markdown(f'<div class="{class_name}">{day}</div>', unsafe_allow_html=True)

    return selected_dates

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
    selected_days = render_calendar_interactive(apply_date)
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
