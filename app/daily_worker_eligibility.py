# app/daily_worker_eligibility.py
import streamlit as st # Streamlit 라이브러리를 가져와 웹 앱을 만듭니다.
import pandas as pd # 날짜 범위 생성 등 데이터 처리를 위해 pandas 라이브러리를 가져옵니다.
from datetime import datetime, timedelta, date # 날짜 및 시간 계산을 위한 datetime 모듈을 가져옵니다.
import calendar # 달력 생성 및 요일 처리를 위한 calendar 모듈을 가져옵니다.
import pytz # 시간대(timezone) 처리를 위한 pytz 라이브러리를 가져옵니다.
import time # 타임스탬프 생성을 위해 time 모듈을 가져옵니다.

# 달력 시작 요일 설정
calendar.setfirstweekday(calendar.SUNDAY) # 달력의 첫 번째 요일을 일요일로 설정합니다.

# KST 시간대 설정
KST = pytz.timezone('Asia/Seoul') # 한국 표준시(KST) 시간대 객체를 생성합니다.
# 현재 시간을 KST로 설정 (고정된 날짜와 시간 사용)
current_datetime = datetime(2025, 5, 29, 20, 15, tzinfo=KST)
# 현재 시간을 한국어 형식의 문자열로 포맷합니다.
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %H:%M KST')

# 스타일시트 로드 (캐시 방지 쿼리 추가)
timestamp = time.time() # 현재 타임스탬프를 가져와 캐시 방지 쿼리로 사용합니다. (현재 코드에서는 사용되지 않음)
with open("static/styles.css") as f: # static/styles.css 파일을 읽기 모드로 엽니다.
    # CSS 파일 내용을 읽어 Streamlit 앱에 스타일로 적용합니다.
    # unsafe_allow_html=True는 HTML/CSS 삽입을 허용합니다.
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 초일부터 신청일까지의 날짜 범위를 반환합니다."""
    # 신청일(apply_date)이 속한 달의 1일로 이동합니다.
    # 그 다음 한 달 전으로 이동한 후 다시 1일로 설정하여 시작 날짜를 계산합니다.
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    # 시작 날짜부터 신청일까지의 모든 날짜를 포함하는 리스트를 반환합니다.
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar(apply_date):
    """달력을 렌더링하고 날짜 선택 기능을 제공합니다."""
    # 'selected_dates' 세션 상태 변수가 없으면 빈 세트로 초기화합니다.
    # 선택된 날짜들을 저장합니다. (세트는 중복을 허용하지 않음)
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates # 현재 선택된 날짜들을 가져옵니다.
    current_date = current_datetime.date() # 현재 날짜를 가져옵니다.
    # 신청일 기준 이전 달 초일 계산 (get_date_range와 동일)
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    # 시작 날짜부터 신청일까지 포함되는 모든 월(year, month)의 고유한 조합을 가져옵니다.
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=apply_date)))

    # 각 월에 대해 반복하여 달력을 렌더링합니다.
    for year, month in months:
        # 현재 월의 헤더를 마크다운으로 출력합니다.
        st.markdown(f"### {year}년 {month}월", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month) # 해당 월의 주별 달력(일자 리스트)을 가져옵니다.
        days_of_week = ["일", "월", "화", "수", "목", "금", "토"] # 요일 이름 리스트를 정의합니다.

        # 요일 헤더를 위한 컨테이너를 생성합니다.
        with st.container():
            # 7개의 작은 컬럼을 생성하여 요일을 배치합니다.
            cols = st.columns(7, gap="small")
            # 각 요일에 대해 반복합니다.
            for i, day in enumerate(days_of_week):
                with cols[i]: # 해당 요일 컬럼 내에 요일 이름을 표시합니다.
                    class_name = "day-header" # 기본 CSS 클래스입니다.
                    if i == 0 or i == 6: # 일요일(0) 또는 토요일(6)인 경우 'weekend' 클래스를 추가합니다.
                        class_name += " weekend"
                    # 요일 이름을 포함하는 div를 마크다운으로 출력합니다.
                    st.markdown(f'<div class="{class_name}">{day}</div>', unsafe_allow_html=True)

        # 날짜 렌더링
        # 주별로 반복합니다.
        for week in cal:
            with st.container(): # 각 주를 위한 컨테이너를 생성합니다.
                cols = st.columns(7, gap="small") # 각 날짜를 위한 7개의 작은 컬럼을 생성합니다.
                # 주 내의 각 날짜에 대해 반복합니다.
                for i, day in enumerate(week):
                    with cols[i]: # 해당 날짜 컬럼 내에서 처리합니다.
                        if day == 0: # day가 0이면 해당 월에 속하지 않는 날짜이므로 빈 칸을 만듭니다.
                            st.empty() # 빈 위젯을 렌더링합니다.
                            continue # 다음 날짜로 넘어갑니다.
                        date_obj = date(year, month, day) # 현재 날짜(정수)로 date 객체를 생성합니다.
                        is_selected = date_obj in selected_dates # 이 날짜가 이미 선택되었는지 확인합니다.
                        is_current = date_obj == current_date # 이 날짜가 오늘 날짜인지 확인합니다.
                        is_disabled = date_obj > apply_date # 이 날짜가 신청일보다 미래인지 확인하여 비활성화 여부를 결정합니다.

                        class_name = "day" # 기본 CSS 클래스입니다.
                        if is_selected: # 선택된 날짜인 경우 'selected' 클래스를 추가합니다.
                            class_name += " selected"
                        if is_current: # 오늘 날짜인 경우 'current' 클래스를 추가합니다.
                            class_name += " current"
                        if is_disabled: # 비활성화된 날짜인 경우 'disabled' 클래스를 추가합니다.
                            class_name += " disabled"

                        with st.container(): # 날짜를 위한 컨테이너를 생성합니다.
                            if is_disabled: # 비활성화된 날짜는 체크박스 없이 텍스트만 표시합니다.
                                st.markdown(f'<div class="{class_name}">{day}</div>', unsafe_allow_html=True)
                            else: # 활성화된 날짜는 체크박스와 함께 날짜를 표시합니다.
                                with st.container():
                                    checkbox_key = f"date_{date_obj}" # 체크박스의 고유 키를 생성합니다.
                                    # 숨겨진 체크박스를 생성합니다. (라벨 없음, 초기 선택 상태 반영)
                                    checkbox_value = st.checkbox(
                                        "", key=checkbox_key, value=is_selected, label_visibility="hidden"
                                    )
                                    # 날짜 div를 마크다운으로 출력합니다. data-date 속성을 추가하여 JS에서 활용 가능하게 합니다.
                                    st.markdown(
                                        f'<div class="{class_name}" data-date="{date_obj}">{day}</div>',
                                        unsafe_allow_html=True
                                    )
                                    # 체크박스 값이 변경되었는지 확인합니다.
                                    if checkbox_value != is_selected:
                                        if checkbox_value: # 체크박스가 선택되면 날짜를 추가합니다.
                                            selected_dates.add(date_obj)
                                        else: # 체크박스가 해제되면 날짜를 제거합니다.
                                            selected_dates.discard(date_obj)
                                        # 세션 상태의 selected_dates를 업데이트합니다.
                                        st.session_state.selected_dates = selected_dates
                                        # 디버깅 로그를 출력합니다.
                                        #st.write(f"Debug: Date {date_obj}, Selected: {checkbox_value}, Class: {class_name}")
                                        st.rerun() # 앱을 재실행하여 UI를 업데이트합니다. (선택 상태 반영)

    # 선택된 근무일자 표시
    if selected_dates: # 선택된 날짜가 하나라도 있으면
        st.markdown("### ✅ 선택된 근무일자") # 제목을 출력합니다.
        # 선택된 날짜들을 정렬하여 "월/일" 형식으로 문자열을 만들고 출력합니다.
        st.markdown(", ".join([d.strftime("%m/%d") for d in sorted(selected_dates)]))

    return st.session_state.selected_dates # 최종 선택된 날짜 세트를 반환합니다.

def daily_worker_eligibility_app():
    """일용근로자 수급자격 요건 모의계산 앱."""
    st.header("일용근로자 수급자격 요건 모의계산") # 앱의 메인 헤더를 출력합니다.

    # 현재 날짜 및 시간 표시
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    # 요건 조건 섹션
    st.markdown("### 📋 요건 조건") # 요건 조건 섹션의 헤더를 출력합니다.
    # 조건 1에 대한 설명을 마크다운으로 출력합니다.
    st.markdown("- **조건 1**: 수급자격 인정신청일의 직전 달 초일부터 신청일까지의 근무일 수가 총 일의 1/3 미만이어야 합니다.")
    # 조건 2에 대한 설명을 마크다운으로 출력합니다. (건설일용근로자만 해당)
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---") # 구분선을 출력합니다.

    # 수급자격 신청일 선택 입력 위젯
    # 기본값은 현재 날짜이고, 고유 키를 지정합니다.
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")

    # get_date_range 함수를 호출하여 날짜 범위와 시작일을 가져옵니다.
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---") # 구분선을 출력합니다.
    st.markdown("#### 근무일 선택 달력") # 달력 섹션의 헤더를 출력합니다.
    # render_calendar 함수를 호출하여 달력을 렌더링하고 선택된 날짜들을 가져옵니다.
    selected_dates = render_calendar(apply_date)
    st.markdown("---") # 구분선을 출력합니다.

    # 조건 1 계산
    total_days = len(date_range_objects) # 계산 대상 기간의 총 일수를 계산합니다.
    worked_days = len(selected_dates) # 선택된 근무일 수를 계산합니다.
    threshold = total_days / 3 # 총 일수의 1/3을 계산합니다.

    st.markdown(f"- 총 기간 일수: **{total_days}일**") # 총 기간 일수를 출력합니다.
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**") # 기준 일수를 소수점 첫째 자리까지 출력합니다.
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**") # 선택한 근무일 수를 출력합니다.

    condition1 = worked_days < threshold # 조건 1 충족 여부를 판단합니다.
    # 조건 1 충족/불충족 결과를 result-text 클래스를 사용하여 출력합니다.
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 1 충족: 근무일 수가 기준 미만입니다." if condition1 else "❌ 조건 1 불충족: 근무일 수가 기준 이상입니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # 조건 2 계산 (건설일용근로자)
    # 신청일 직전 14일 기간의 마지막 날짜를 계산합니다. (신청일 제외)
    fourteen_days_prior_end = apply_date - timedelta(days=1)
    # 신청일 직전 14일 기간의 시작 날짜를 계산합니다.
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    # 14일간의 날짜 범위 리스트를 생성합니다.
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    # 14일 기간 동안 선택된 근무일이 하나도 없는지 확인합니다.
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days # 조건 2 충족 여부를 저장합니다.

    # 조건 2 충족/불충족 결과를 result-text 클래스를 사용하여 출력합니다.
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 2 충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 근무내역이 없습니다." if no_work_14_days else "❌ 조건 2 불충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 내 근무기록이 존재합니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("---") # 구분선을 출력합니다.

    # 조건 1 불충족 시 미래 신청일 제안
    if not condition1: # 조건 1이 충족되지 않았다면
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?") # 제안 섹션의 헤더를 출력합니다.
        found_suggestion = False # 제안을 찾았는지 여부를 나타내는 플래그입니다.
        # 현재 신청일로부터 최대 30일 미래까지 탐색합니다.
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i) # 미래 날짜를 계산합니다.
            # 미래 날짜를 기준으로 새로운 날짜 범위와 시작일을 가져옵니다.
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects) # 미래 기준 총 기간 일수를 계산합니다.
            threshold_future = total_days_future / 3 # 미래 기준 1/3 임계값을 계산합니다.
            # 미래 날짜까지의 선택된 근무일 수를 계산합니다.
            worked_days_future = sum(1 for d in selected_dates if d <= future_date)

            if worked_days_future < threshold_future: # 미래 날짜에 조건 1이 충족되는지 확인합니다.
                # 충족될 경우 제안 메시지를 출력합니다.
                st.markdown(
                    f'<div class="result-text">'
                    f'<p>✅ <b>{future_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 요건을 충족할 수 있습니다.</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                found_suggestion = True # 제안을 찾았음을 표시합니다.
                break # 제안을 찾았으므로 루프를 종료합니다.
        if not found_suggestion: # 30일 이내에 제안을 찾지 못했다면
            # 충족 불가능 메시지를 출력합니다.
            st.markdown(
                f'<div class="result-text">'
                f'<p>❗ 앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    # 조건 2 불충족 시 미래 신청일 제안
    if not condition2: # 조건 2가 충족되지 않았다면
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?") # 제안 섹션의 헤더를 출력합니다.
        # 선택된 근무일 중 신청일 이전의 마지막 근무일을 찾습니다.
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day: # 마지막 근무일이 존재한다면
            # 마지막 근무일로부터 15일 뒤를 제안 신청일로 계산합니다. (14일간 근무 사실이 없어야 하므로 15일째가 되어야 함)
            suggested_date = last_worked_day + timedelta(days=15)
            # 제안 메시지를 출력합니다.
            st.markdown(
                f'<div class="result-text">'
                f'<p>✅ <b>{suggested_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 조건 2를 충족할 수 있습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )
        else: # 마지막 근무일이 없다면 (선택된 근무일이 없거나 모두 신청일 이후인 경우)
            # 이미 조건 2를 충족하고 있음을 알리는 메시지를 출력합니다.
            st.markdown(
                f'<div class="result-text">'
                f'<p>이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.subheader("📌 최종 판단") # 최종 판단 섹션의 헤더를 출력합니다.
    # 일반일용근로자: 조건 1만으로 판단
    if condition1: # 조건 1이 충족되면 일반일용근로자는 신청 가능합니다.
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 일반일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else: # 조건 1이 충족되지 않으면 일반일용근로자는 신청 불가능합니다.
        st.markdown(
            f'<div class="result-text">'
            f'<p>❌ 일반일용근로자: 신청 불가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )

    # 건설일용근로자: 조건 1과 2 모두 충족해야 판단
    if condition1 and condition2: # 조건 1과 조건 2 모두 충족되면 건설일용근로자는 신청 가능합니다.
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 건설일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간({fourteen_days_prior_start.strftime("%Y-%m-%d")} ~ {fourteen_days_prior_end.strftime("%Y-%m-%d")}) 근무 사실이 없음을 확인합니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else: # 둘 중 하나라도 충족되지 않으면 건설일용근로자는 신청 불가능합니다.
        error_message = "❌ 건설일용근로자: 신청 불가능<br>" # 오류 메시지 기본 내용을 설정합니다.
        if not condition1: # 조건 1이 불충족이면 해당 사유를 메시지에 추가합니다.
            error_message += f"<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b><br>"
        if not condition2: # 조건 2가 불충족이면 해당 사유를 메시지에 추가합니다.
            error_message += f"<b>신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 있습니다.</b>"
        # 최종 오류 메시지를 result-text 클래스를 사용하여 출력합니다.
        st.markdown(
            f'<div class="result-text">'
            f'<p>{error_message}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

# 이 스크립트가 직접 실행될 때 daily_worker_eligibility_app 함수를 호출합니다.
if __name__ == "__main__":
    daily_worker_eligibility_app()
