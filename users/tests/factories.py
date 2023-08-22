import factory
from factory.django import DjangoModelFactory


class UserPublicFactory(DjangoModelFactory):
    external_user_uid = factory.Faker("uuid4")
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    is_active = True

    class Meta:
        model = "users.UserPublic"
