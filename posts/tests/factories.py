import factory
from factory.django import DjangoModelFactory

from users.tests.factories import UserPublicFactory


class PostFactory(DjangoModelFactory):
    user = factory.SubFactory(UserPublicFactory)
    title = factory.Faker("text")
    content = factory.Faker("text")

    class Meta:
        model = "posts.Post"


class PostVoteFactory(DjangoModelFactory):
    user = factory.SubFactory(UserPublicFactory)
    post = factory.SubFactory(PostFactory)

    class Meta:
        model = "posts.PostVote"
