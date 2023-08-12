from rest_framework import serializers


class WritableSlugRelatedField(serializers.SlugRelatedField):
    """Extending SlugRelatedField to make it writable."""

    def to_internal_value(self, data):
        """Convert data to internal value."""
        try:
            instance, _ = self.get_queryset().get_or_create(**{self.slug_field: data})
            return instance
        except (TypeError, ValueError):
            self.fail("invalid")
