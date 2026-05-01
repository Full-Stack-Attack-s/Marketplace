from django.core.exceptions import ValidationError

def validate_image_size(file):
    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Максимальный размер файла — {max_size_mb} МБ. Текущий размер: {round(file.size / (1024 * 1024), 2)} МБ.")
