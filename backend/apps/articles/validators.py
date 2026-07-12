import os

from rest_framework import serializers

# TS section 5 ("допустимые форматы файлов (например, doc/docx/pdf)") names
# these three as an example, not an exhaustive list — kept literal since the
# spec gives no other candidates. Size cap (20 MB) isn't specified in TS
# either; picked as a reasonable ceiling for an academic manuscript.
ALLOWED_MANUSCRIPT_EXTENSIONS = {".doc", ".docx", ".pdf"}
MAX_MANUSCRIPT_SIZE_BYTES = 20 * 1024 * 1024


def validate_manuscript_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_MANUSCRIPT_EXTENSIONS:
        raise serializers.ValidationError(
            f"Недопустимый формат файла. Разрешены: {', '.join(sorted(ALLOWED_MANUSCRIPT_EXTENSIONS))}."
        )
    if file.size > MAX_MANUSCRIPT_SIZE_BYTES:
        raise serializers.ValidationError(
            f"Файл слишком большой. Максимальный размер — {MAX_MANUSCRIPT_SIZE_BYTES // (1024 * 1024)} МБ."
        )
