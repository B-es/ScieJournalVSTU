from rest_framework import serializers

from .models import Issue


class IssueSerializer(serializers.ModelSerializer):
    """Read shape for the {issueId} response and any future issue listing."""

    descriptionRu = serializers.CharField(source="description_ru")
    descriptionEn = serializers.CharField(source="description_en")
    coverImageUrl = serializers.ImageField(source="cover_image", use_url=True)
    publishedAt = serializers.DateTimeField(source="published_at")

    class Meta:
        model = Issue
        fields = ["id", "number", "year", "title", "descriptionRu", "descriptionEn", "coverImageUrl", "publishedAt", "language"]


class IssueCreateInputSerializer(serializers.Serializer):
    """
    POST /api/issues (TS section 7, US-9) — thin wrapper around what
    Django Admin's IssueAdmin (M1) already does; see M3f plan decision #3.
    """

    number = serializers.IntegerField(min_value=1)
    year = serializers.IntegerField(min_value=1)
    descriptionRu = serializers.CharField(required=False, allow_blank=True, default="")
    descriptionEn = serializers.CharField(required=False, allow_blank=True, default="")
    coverImage = serializers.ImageField(required=False)

    def validate(self, attrs):
        # Issue has a (number, year) unique_together constraint (M1) — check
        # here rather than letting Issue.objects.create() raise a raw
        # IntegrityError (500) for a plainly foreseeable duplicate input.
        if Issue.objects.filter(number=attrs["number"], year=attrs["year"]).exists():
            raise serializers.ValidationError("Выпуск с таким номером и годом уже существует.")
        return attrs
