import factory
from factory.django import DjangoModelFactory


class UserPublicFactory(DjangoModelFactory):
    external_user_uid = factory.Faker("text", max_nb_chars=32)
    username = factory.Faker("text", max_nb_chars=100)
    is_active = True

    class Meta:
        model = "users.UserPublic"
