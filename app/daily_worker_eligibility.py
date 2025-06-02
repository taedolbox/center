import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import pytz
import time

# 달력 시작 요일 설정
calendar.setfirstweekday(calendar.SUNDAY)

# KST 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 스타일시트 로드 (캐시 방지 쿼리 추가)
# 이 부분은 변경 없음. styles.css 파일이 정상적으로 로드되는지 확인합니다.
timestamp = time.time()
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 초일부터 신청일까지의 날짜 범위를 반환합니다."""
    # 신청일이 포함된 달의 첫 날
    start_of_apply_month = apply_date.replace(day=1)
    # 신청일 직전 달의 첫 날
    start_date = (start_of_apply_month - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar(apply_date):
    """달력을 렌더링하고 날짜 선택 기능을 제공합니다."""
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now(KST).date()
    
    # 달력에 표시할 월 범위 결정: 신청일 직전 달 초일부터 신청일이 포함된 달까지
    start_of_prev_month = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    
    # apply_date까지 포함하는 월들을 추출
    months_to_render = sorted(set((d.year, d.month) for d in pd.date_range(start=start_of_prev_month, end=apply_date)))

    for year, month in months_to_render:
        st.markdown(f"### {year}년 {month}월", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        
        # 요일 헤더 렌더링
        with st.container():
            day_headers = ["일", "월", "화", "수", "목", "금", "토"]
            cols = st.columns(7, gap="small") # Streamlit의 컬럼 간격
            for i, day_name in enumerate(day_headers):
                with cols[i]:
                    class_name = "day-header"
                    if i == 0: # 일요일
                        class_name += " sunday"
                    elif i == 6: # 토요일
                        class_name += " saturday"
                    st.markdown(f'<div class="{class_name}">{day_name}</div>', unsafe_allow_html=True)

        # 날짜 렌더링
        for week in cal:
            with st.container():
                cols = st.columns(7, gap="small") # Streamlit의 컬럼 간격
                for i, day in enumerate(week):
                    with cols[i]:
                        if day == 0: # 해당 월에 속하지 않는 날짜 (빈 칸)
                            st.empty()
                            continue
                        
                        date_obj = date(year, month, day)
                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date
                        # 'is_disabled'는 신청일 이후의 날짜를 의미하며, 이 날짜는 선택할 수 없도록 합니다.
                        is_disabled = date_obj > apply_date 

                        class_name = "day"
                        if is_selected:
                            class_name += " selected"
                        if is_current:
                            class_name += " current"
                        if is_disabled:
                            class_name += " disabled" # disabled 클래스 추가
                        if i == 0: # 일요일
                            class_name += " sunday"
                        elif i == 6: # 토요일
                            class_name += " saturday"
                        
                        # --- 핵심 변경 부분: 모든 날짜에 대해 동일한 HTML 구조를 사용 ---
                        # Streamlit 체크박스를 항상 렌더링하되, disabled 상태일 때는 비활성화합니다.
                        # CSS에서 이 체크박스를 숨겨서 시각적으로는 보이지 않게 합니다.
                        checkbox_key = f"date_{date_obj}"
                        checkbox_value = st.checkbox(
                            "",
                            key=checkbox_key,
                            value=is_selected,
                            label_visibility="hidden",
                            disabled=is_disabled # 신청일 이후 날짜는 체크박스 비활성화
                        )
                        
                        # 날짜 숫자(원형)를 나타내는 div는 항상 렌더링
                        st.markdown(
                            f'<div class="{class_name}" data-date="{date_obj}">{day}</div>',
                            unsafe_allow_html=True
                        )
                        
                        # 체크박스 값 변경 감지 (비활성화되지 않은 경우에만)
                        if not is_disabled and checkbox_value != is_selected:
                            if checkbox_value:
                                selected_dates.add(date_obj)
                            else:
                                selected_dates.discard(date_obj)
                            st.session_state.selected_dates = selected_dates
                            st.rerun() # 상태 변경 시 Streamlit 앱 새로고침

    # 선택된 근무일자 표시
    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%m/%d") for d in sorted(selected_dates)]))

    return st.session_state.selected_dates

def daily_worker_eligibility_app():
    """일용근로자 수급자격 요건 모의계산 앱."""
    st.header("일용근로자 수급자격 요건 모의계산")

    # 오늘 날짜로 수정을 했습니다: Streamlit 앱이 재실행될 때마다 현재 날짜와 시간을 KST 기준으로 정확히 가져옵니다.
    current_datetime = datetime.now(KST)
    current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')

    # 현재 날짜 및 시간 표시
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    # 요건 조건
    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일의 직전 달 초일부터 신청일까지의 근무일 수가 총 일의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    # 수급자격 신청일 선택
    # 오늘 날짜로 수정을 했습니다: st.date_input의 기본값도 현재 날짜를 따르도록 합니다.
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")

    # 날짜 범위 및 시작일 가져오기
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### 근무일 선택 달력")
    selected_dates = render_calendar(apply_date) # 달력 렌더링 함수 호출
    st.markdown("---")

    # 조건 1 계산
    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 1 충족: 근무일 수가 기준 미만입니다." if condition1 else "❌ 조건 1 불충족: 근무일 수가 기준 이상입니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # 조건 2 계산 (건설일용근로자)
    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 2 충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 근무내역이 없습니다." if no_work_14_days else "❌ 조건 2 불충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 내 근무기록이 존재합니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # 조건 1 불충족 시 미래 신청일 제안
    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        found_suggestion = False
        for i in range(1, 31): # 향후 30일까지 확인
            future_date = apply_date + timedelta(days=i)
            # 미래 날짜 기준으로 날짜 범위 재계산
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            # 미래 날짜까지의 근무일만 카운트
            worked_days_future = sum(1 for d in selected_dates if d <= future_date)

            if worked_days_future < threshold_future:
                st.markdown(
                    f'<div class="result-text">'
                    f'<p>✅ <b>{future_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 요건을 충족할 수 있습니다.</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                found_suggestion = True
                break
        if not found_suggestion:
            st.markdown(
                f'<div class="result-text">'
                f'<p>❗ 앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    # 조건 2 불충족 시 미래 신청일 제안
    if not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        # 선택된 날짜 중 신청일 이전의 가장 최근 근무일
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15) # 마지막 근무일 + 14일 + 1일
            st.markdown(
                f'<div class="result-text">'
                f'<p>✅ <b>{suggested_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 조건 2를 충족할 수 있습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="result-text">'
                f'<p>이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.subheader("📌 최종 판단")
    # 일반일용근로자: 조건 1만 만족하면 됨
    if condition1:
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 일반일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="result-text">'
            f'<p>❌ 일반일용근로자: 신청 불가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )

    # 건설일용근로자: 조건 1과 조건 2 모두 만족해야 함
    if condition1 and condition2:
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 건설일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간({fourteen_days_prior_start.strftime("%Y-%m-%d")} ~ {fourteen_days_prior_end.strftime("%Y-%m-%d")}) 근무 사실이 없음을 확인합니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        error_message = "❌ 건설일용근로자: 신청 불가능<br>"
        if not condition1:
            error_message += f"<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b><br>"
        if not condition2:
            error_message += f"<b>신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 있습니다.</b>"
        st.markdown(
            f'<div class="result-text">'
            f'<p>{error_message}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    daily_worker_eligibility_app()

