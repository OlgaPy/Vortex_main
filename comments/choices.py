from django.db import models


class Vote(models.IntegerChoices):
    UPVOTE = 1
    DOWNVOTE = -1
