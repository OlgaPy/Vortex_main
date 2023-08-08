import factory
from factory.django import DjangoModelFactory


class UserPublicFactory(DjangoModelFactory):
    external_user_uid = factory.Faker("text", max_nb_chars=32)

    class Meta:
        model = "users.UserPublic"


class PostFactory(DjangoModelFactory):
    user = factory.SubFactory(UserPublicFactory)
    title = factory.Faker("text")
    content = factory.Faker("text")

    class Meta:
        model = "users.Post"


class CommentFactory(DjangoModelFactory):
    user = factory.SubFactory(UserPublicFactory)
    post = factory.SubFactory(PostFactory)
    content = factory.Faker("text")

    class Meta:
        model = "users.Comment"


class PostVoteFactory(DjangoModelFactory):
    user = factory.SubFactory(UserPublicFactory)
    post = factory.SubFactory(PostFactory)

    class Meta:
        model = "users.PostVote"


class CommentVoteFactory(DjangoModelFactory):
    user = factory.SubFactory(UserPublicFactory)
    comment = factory.SubFactory(CommentFactory)

    class Meta:
        model = "users.CommentVote"
