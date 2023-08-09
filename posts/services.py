from django.db.models import F

from posts.choices import Vote
from posts.models import PostVote, CommentVote


def update_author_rating_on_post_vote(vote: PostVote):
    author = vote.post.user
    author.rating = F("rating") + vote.value
    author.save(update_fields=["rating"])


def update_author_rating_on_post_vote_delete(vote: PostVote):
    ...


def update_author_rating_on_comment_vote_delete(vote: CommentVote):
    ...


def update_author_rating_on_comment_vote(vote: CommentVote):
    author = vote.comment.user
    author.rating = F("rating") + vote.value / 2
    author.save(update_fields=["rating"])


def update_post_rating_on_vote(vote: PostVote):
    post = vote.post
    post.rating = F("rating") + vote.value
    if vote == Vote.UPVOTE:
        post.votes_up_count = F("votes_up_count") + 1
    else:
        post.votes_down_count = F("votes_down_count") + 1


def update_post_rating_on_vote_delete(vote: PostVote):
    ...


def update_comment_rating_on_vote(vote: CommentVote):
    ...


def update_comment_rating_on_vote_delete(vote: CommentVote):
    ...
