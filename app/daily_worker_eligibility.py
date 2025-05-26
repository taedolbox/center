# daily_worker_eligibility.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

calendar.setfirstweekday(calendar.SUNDAY)
current_datetime = datetime(2025, 5, 26, 6, 29)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오전 %I:%M KST')

def get_date_range(apply_date):
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    with st.container():
        st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
        for year, month in months_to_display:
            st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
            cal = calendar.monthcalendar(year, month)
            days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

            cols = st.columns(7, gap="small")
            for i, day_name in enumerate(days_of_week_korean):
                with cols[i]:
                    color = "red" if i == 0 or i == 6 else "#000000"
                    st.markdown(
                        f'<div class="day-header"><span style="color: {color}">{day_name}</span></div>',
                        unsafe_allow_html=True
                    )

            for week in cal:
                cols = st.columns(7, gap="small")
                for i, day in enumerate(week):
                    with cols[i]:
                        if day == 0:
                            st.markdown('<div class="calendar-day-container"></div>', unsafe_allow_html=True)
                            continue
                        date_obj = date(year, month, day)
                        if date_obj > apply_date:
                            st.markdown(
                                f'<div class="calendar-day-container">'
                                f'<div class="calendar-day-box disabled-day">{day}</div>'
                                f'<button data-testid="stButton" style="display: none;"></button>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                            continue

                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date
                        class_name = "calendar-day-box"
                        if is_selected:
                            class_name += " selected-day"
                        if is_current:
                            class_name += " current-day"

                        container_key = f"date_{date_obj.isoformat()}"
                        st.markdown(
                            f'<div class="calendar-day-container">'
                            f'<div class="selection-mark"></div>'
                            f'<div class="{class_name}">{day}</div>'
                            f'<button data-testid="stButton" key="{container_key}" onClick="window.parent.window.dispatchEvent(new Event(\'button_click_{container_key}\'));"></button>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        if st.button("", key=container_key, on_click=toggle_date, args=(date_obj,), use_container_width=True):
                            pass
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.rerun_trigger:
        st.session_state.rerun_trigger = False
        st.rerun()

    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    return st.session_state.selected_dates

def toggle_date(date_obj):
    if date_obj in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(date_obj)
    else:
        st.session_state.selected_dates.add(date_obj)
    st.session_state.rerun_trigger = True

def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 신청일 기준 직전달 1일부터 신청일까지의 근로일 수가 총일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자)**: 신청일 직전 14일간 근무 사실이 없어야 합니다.")
    st.markdown("---")

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_dates = render_calendar_interactive(apply_date)
    st.markdown("---")

    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (1/3): **{threshold:.1f}일**")
    st.markdown(f"- 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 1 충족" if condition1 else "❌ 조건 1 불충족"}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 2 충족" if condition2 else "❌ 조건 2 불충족"}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    if not condition1:
        st.markdown("### 조건 1을 만족하려면?")
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_dates if d <= future_date)
            if worked_days_future < threshold_future:
                st.markdown(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후 신청 시 조건 1을 만족합니다.")
                break
        else:
            st.markdown("❗ 30일 내 조건 1 만족 불가. 더 미래의 날짜가 필요합니다.")

    if not condition2:
        st.markdown("### 조건 2를 만족하려면?")
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.markdown(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후 신청 시 조건 2 만족.")
        else:
            st.markdown("이미 최근 14일 근무 없음 → 신청일 조정 불필요.")

    st.subheader("📌 최종 판단")
    if condition1:
        st.markdown("✅ 일반일용근로자: 신청 가능")
    else:
        st.markdown("❌ 일반일용근로자: 신청 불가")

    if condition1 and condition2:
        st.markdown("✅ 건설일용근로자: 신청 가능")
    else:
        st.markdown("❌ 건설일용근로자: 신청 불가")

if __name__ == "__main__":
    daily_worker_eligibility_app()
