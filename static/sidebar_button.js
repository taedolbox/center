// static/sidebar_button.js
document.addEventListener('DOMContentLoaded', (event) => {
    function updateSidebarButtonText() {
        // stSidebarCollapsedControl div 내부의 버튼을 찾습니다.
        // 이것이 실제 사이드바 열기/닫기 버튼일 가능성이 높습니다.
        const sidebarControlDiv = document.querySelector('div[data-testid="stSidebarCollapsedControl"]');
        let sidebarButton = null;

        if (sidebarControlDiv) {
            // 해당 div 내부에 있는 data-testid="stBaseButton-headerNoPadding" 버튼을 찾습니다.
            sidebarButton = sidebarControlDiv.querySelector('button[data-testid="stBaseButton-headerNoPadding"]');
        }

        if (sidebarButton) {
            // aria-expanded 속성을 통해 사이드바가 열려있는지 닫혀있는지 확인합니다.
            // Streamlit은 사이드바가 열리면 이 속성을 "true"로 설정하고, 닫히면 "false"로 설정합니다.
            const isSidebarExpanded = sidebarButton.getAttribute('aria-expanded') === 'true';

            if (isSidebarExpanded) {
                sidebarButton.setAttribute('aria-label', '메뉴 닫기'); // 웹 접근성을 위해 aria-label도 변경
                sidebarButton.innerHTML = '메뉴닫기';
            } else {
                sidebarButton.setAttribute('aria-label', '메뉴 열기'); // 웹 접근성을 위해 aria-label도 변경
                sidebarButton.innerHTML = '메뉴열기';
            }
        }
    }

    // 초기 실행
    updateSidebarButtonText();

    // MutationObserver를 사용하여 DOM 변경 감지
    // Streamlit이 UI를 다시 렌더링하거나 사이드바 상태가 변경될 때 버튼 텍스트가 유지되도록 합니다.
    const observer = new MutationObserver(updateSidebarButtonText);
    const config = {
        childList: true,   // 자식 노드 추가/제거 감지
        subtree: true,     // 모든 하위 노드까지 감지
        attributes: true,  // 속성 변경 감지
        attributeFilter: ['aria-expanded', 'aria-label', 'data-testid'] // 특정 속성만 필터링하여 효율성 높임
    };

    // document.body 전체를 관찰 시작 (Streamlit의 동적 렌더링에 대응)
    observer.observe(document.body, config);
});
