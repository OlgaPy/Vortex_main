from django.db import models


class CommentVote(models.IntegerChoices):
    UPVOTE = 1
    DOWNVOTE = -1
