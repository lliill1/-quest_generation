document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const fileDisplay = document.getElementById('file-display');
    const uploadArea = document.getElementById('upload-area');
    const submitBtn = document.getElementById('submit-btn');
    
    // Обработка выбора файла
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileDisplay.innerHTML = `<i class="fas fa-file-alt me-2"></i>Выбран файл: <strong>${e.target.files[0].name}</strong>`;
            submitBtn.disabled = false;
            uploadArea.style.borderColor = 'var(--primary)';
        }
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = 'rgba(255, 42, 109, 0.15)';
        uploadArea.style.borderColor = 'var(--primary)';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.backgroundColor = '';
        uploadArea.style.borderColor = 'var(--border)';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = '';
        uploadArea.style.borderColor = 'var(--primary)';
        
        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.name.endsWith('.txt')) {
                // Создаем новый DataTransfer для установки файла
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;
                
                fileDisplay.innerHTML = `<i class="fas fa-file-alt me-2"></i>Выбран файл: <strong>${file.name}</strong>`;
                submitBtn.disabled = false;
            } else {
                fileDisplay.innerHTML = '<span class="text-danger"><i class="fas fa-exclamation-circle me-2"></i>Ошибка: файл должен быть в формате .txt</span>';
                submitBtn.disabled = true;
            }
        }
    });
});