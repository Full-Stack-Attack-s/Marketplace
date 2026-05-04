document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('productSearch');
    const statusFilter = document.getElementById('statusFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const stockFilter = document.getElementById('stockFilter');
    const table = document.getElementById('productsTable');
    const rows = table?.querySelectorAll('.product-row');
    
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.product-checkbox');
    const bulkBar = document.getElementById('bulkActionsBar');
    const selectedCount = document.getElementById('selectedCount');

    function updateBulkBar() {
        if (!bulkBar || !selectedCount) return;
        const checked = document.querySelectorAll('.product-checkbox:checked');
        if (checked.length > 0) {
            bulkBar.style.display = 'flex';
            selectedCount.textContent = checked.length;
        } else {
            bulkBar.style.display = 'none';
        }
    }

    if (selectAll) {
        selectAll.addEventListener('change', function() {
            checkboxes.forEach(cb => {
                if (cb.closest('tr').style.display !== 'none') {
                    cb.checked = this.checked;
                }
            });
            updateBulkBar();
        });
    }

    checkboxes.forEach(cb => {
        cb.addEventListener('change', updateBulkBar);
    });

    window.submitBulkAction = function(action) {
        const checked = document.querySelectorAll('.product-checkbox:checked');
        if (checked.length === 0) return;

        let confirmMsg = `Применить действие "${action}" к ${checked.length} товарам?`;
        if (action === 'delete') confirmMsg = `ВНИМАНИЕ! Вы уверены, что хотите УДАЛИТЬ ${checked.length} товаров? Это действие необратимо.`;
        
        if (!confirm(confirmMsg)) return;

        const form = document.getElementById('bulkActionForm');
        const container = document.getElementById('bulkIdsContainer');
        const actionInput = document.getElementById('bulkActionInput');

        if (!form || !container || !actionInput) return;

        actionInput.value = action;
        container.innerHTML = '';
        checked.forEach(cb => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'product_ids';
            input.value = cb.value;
            container.appendChild(input);
        });

        form.submit();
    };

    function filterProducts() {
        if (!rows) return;
        const query = searchInput?.value.toLowerCase() || '';
        const status = statusFilter?.value || 'all';
        const category = categoryFilter?.value || 'all';
        const stockMode = stockFilter?.value || 'all';

        rows.forEach(row => {
            const name = row.querySelector('.p-name')?.textContent.toLowerCase() || '';
            const sku = row.querySelector('.p-sku')?.textContent.toLowerCase() || '';
            const rowStatus = row.dataset.status;
            const rowCategory = row.dataset.category;
            const rowStock = parseInt(row.dataset.stock) || 0;

            const matchesSearch = name.includes(query) || sku.includes(query);
            const matchesStatus = status === 'all' || rowStatus === status;
            const matchesCategory = category === 'all' || rowCategory === category;
            
            let matchesStock = true;
            if (stockMode === 'in_stock') matchesStock = rowStock > 0;
            else if (stockMode === 'low_stock') matchesStock = rowStock > 0 && rowStock <= 5;
            else if (stockMode === 'out_of_stock') matchesStock = rowStock === 0;

            if (matchesSearch && matchesStatus && matchesCategory && matchesStock) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
                const cb = row.querySelector('.product-checkbox');
                if (cb) cb.checked = false;
            }
        });
        updateBulkBar();
    }

    searchInput?.addEventListener('input', filterProducts);
    statusFilter?.addEventListener('change', filterProducts);
    categoryFilter?.addEventListener('change', filterProducts);
    stockFilter?.addEventListener('change', filterProducts);
});
