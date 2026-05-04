document.addEventListener('DOMContentLoaded', function() {
    const logoInput = document.querySelector('.hidden-file-input');
    if (logoInput) {
        logoInput.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const previewImg = document.getElementById('logo-preview-img');
                    const placeholder = document.getElementById('logo-placeholder');
                    const container = document.querySelector('.logo-preview-container');
                    
                    if (previewImg) {
                        previewImg.src = e.target.result;
                    } else if (placeholder) {
                        placeholder.remove();
                        const img = document.createElement('img');
                        img.id = 'logo-preview-img';
                        img.className = 'logo-preview-img';
                        img.src = e.target.result;
                        container.prepend(img);
                    }
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
});
