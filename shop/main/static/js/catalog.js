document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.catalog-tab');
    const panes = document.querySelectorAll('.catalog-pane');

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Add active to clicked tab
            this.classList.add('active');

            // Hide all panes
            panes.forEach(p => p.classList.add('hidden'));
            
            // Show target pane
            const targetId = this.getAttribute('data-target');
            const targetPane = document.getElementById(targetId);
            if(targetPane) {
                targetPane.classList.remove('hidden');
            }
        });
    });
});

function toggleCategoryList(btn, listId) {
    const list = document.getElementById(listId);
    if (!list) return;
    const hiddenItems = list.querySelectorAll('.hidden-item');
    const isExpanded = btn.getAttribute('data-expanded') === 'true';

    hiddenItems.forEach(item => {
        item.style.display = isExpanded ? 'none' : 'block';
    });

    if (isExpanded) {
        btn.innerHTML = 'Еще <span class="arrow-down">⌄</span>';
        btn.setAttribute('data-expanded', 'false');
    } else {
        btn.innerHTML = 'Свернуть <span class="arrow-up">⌃</span>';
        btn.setAttribute('data-expanded', 'true');
    }
}
