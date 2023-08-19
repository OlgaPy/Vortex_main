import factory
from factory.django import DjangoModelFactory


class CommentFactory(DjangoModelFactory):
    user = factory.SubFactory("users.tests.factories.UserPublicFactory")
    post = factory.SubFactory("posts.tests.factories.PostFactory")
    content = factory.Faker("text")

    class Meta:
        model = "comments.Comment"


class CommentVoteFactory(DjangoModelFactory):
    user = factory.SubFactory("users.tests.factories.UserPublicFactory")
    comment = factory.SubFactory(CommentFactory)

    class Meta:
        model = "comments.CommentVote"
