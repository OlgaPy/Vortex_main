import operator

from django.db.models import F

from comments.models import Comment


def update_post_comments_count(comment: Comment, added: bool = True):
    """Update comments count fot the post comment posted on."""
    post = comment.post
    operation = {
        True: operator.add,
        False: operator.sub,
    }[added]
    post.comments_count = operation(F("comments_count"), 1)
    post.save(update_fields=["comments_count"])


def update_author_comments_count(comment: Comment, added: bool = True):
    author = comment.user
    operation = {
        True: operator.add,
        False: operator.sub,
    }[added]
    author.comments_count = operation(F("comments_count"), 1)
    author.save(update_fields=["comments_count"])
