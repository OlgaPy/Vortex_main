import datetime
import os
import uuid

from django.db import models
from django.utils.deconstruct import deconstructible


@deconstructible
class upload_to:
    """Class to be added to ``upload_to`` property on FileField and ImageField.

    Allows to control how files will be stored and what name will be generated.
    Can take name from the model instance itself in case ``model_field_name`` specified,
    otherwise file name would be uuid

    >>> image = models.ImageField(upload_to=upload_to("files/%Y-%m-%d", "id"))
    """

    def __init__(self, base_path: str, model_field_name: str = None):
        """Class initializer, accepting relative path and also model field."""
        self.base_path = base_path
        self.model_field_name = model_field_name

    def __call__(self, instance: models.Model, filename: str):
        """Make class callable, generates file name with path based on model and file."""
        _, ext = os.path.splitext(filename)
        filename = getattr(instance, self.model_field_name, None) or uuid.uuid4()
        return f"{datetime.datetime.now().strftime(self.base_path)}/{filename}{ext}"
