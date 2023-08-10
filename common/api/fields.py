from rest_framework import serializers


class WritableSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            instance, _ = self.get_queryset().get_or_create(**{self.slug_field: data})
            return instance
        except (TypeError, ValueError):
            self.fail("invalid")
