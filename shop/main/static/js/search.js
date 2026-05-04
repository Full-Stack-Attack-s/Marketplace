document.addEventListener('DOMContentLoaded', function() {
    const filtersForm = document.getElementById('filtersForm');
    
    // Авто-отправка формы при изменении радио-кнопок и чекбоксов
    if (filtersForm) {
        filtersForm.querySelectorAll('input[type="radio"], input[type="checkbox"]').forEach(input => {
            input.addEventListener('change', () => filtersForm.submit());
        });
    }

    // Логика очистки цены
    const priceMin = document.getElementById('priceMin');
    const priceMax = document.getElementById('priceMax');
    
    function setupClearPrice(input) {
        if (!input) return;
        const wrapper = input.parentElement;
        const clearBtn = wrapper.querySelector('.clear-price');
        
        const toggleClear = () => {
            if (clearBtn) clearBtn.style.display = input.value ? 'block' : 'none';
        };

        input.addEventListener('input', toggleClear);
        toggleClear();

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                input.value = '';
                toggleClear();
                // Если нужно сразу отправить форму после очистки:
                // filtersForm.submit();
            });
        }
    }

    setupClearPrice(priceMin);
    setupClearPrice(priceMax);

    // Дерево категорий: сворачивание/разворачивание
    const toggles = document.querySelectorAll('.tree-toggle');
    toggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const node = this.closest('.tree-node');
            node.classList.toggle('collapsed');
            const childTree = node.querySelector('.child-tree');
            if (childTree) {
                childTree.style.display = node.classList.contains('collapsed') ? 'none' : 'block';
            }
        });
    });
});
