from django.db.models import F

from users.models import PostVote, CommentVote


def update_author_rating_on_post_vote(vote: PostVote):
    author = vote.post.user
    author.rating = F("rating") + vote.value
    author.save(update_fields=["rating"])


def update_author_rating_on_comment_vote(vote: CommentVote):
    author = vote.comment.user
    author.rating = F("rating") + vote.value / 2
    author.save(update_fields=["rating"])
