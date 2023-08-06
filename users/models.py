from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.urls import reverse


class UserPrivate(models.Model):
    name = models.CharField(max_length=25, unique=True, null=False, blank=False)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)


class Community(models.Model):
    OPEN = 'O'
    CLOSED = 'C'

    COMMUNITY_STATUS = [
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(UserPrivate, on_delete=models.SET_NULL, null=True, related_name='owned_communities')
    status = models.CharField(max_length=1, choices=COMMUNITY_STATUS, default=OPEN)


class UserPublic(models.Model):
    user = models.OneToOneField(UserPrivate, on_delete=models.CASCADE, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    rating = models.FloatField(default=0)
    followers = models.ManyToManyField('self', related_name='following', symmetrical=False)
    communities = models.ManyToManyField(Community, related_name='users')

    # def get_stats(self):
    #     user = self.user
    #     return {
    #         'userpost_count': user.post_set.count(),
    #         'usercomment_count': user.comment_set.count(),
    #         'userupvotes_count': user.vote_set.filter(vote=1).count(),
    #         'userdownvotes_count': user.vote_set.filter(vote=-1).count(),
    #         'followers_count': self.followers.count(),
    #         'following_users_count': self.following.count(),
    #         'following_communities_count': self.communities.count(),
    #     }


class UserSettings(models.Model):
    user = models.OneToOneField(UserPrivate, on_delete=models.CASCADE, unique=True)
    followed_users = models.ManyToManyField(UserPrivate, related_name='followers', blank=True)
    blocked_users = models.ManyToManyField(UserPrivate, related_name='blocking_users', blank=True)
    subscribed_tags = models.ManyToManyField('Tag', related_name='subscribed_users', blank=True)
    excluded_tags = models.ManyToManyField('Tag', related_name='users_with_excluded', blank=True)
    joined_communities = models.ManyToManyField(Community, related_name='members', blank=True)
    subscribed_communities = models.ManyToManyField(Community, related_name='subscribers', blank=True)


class PostStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(UserPrivate, on_delete=models.CASCADE, related_name='posts')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    video = models.FileField(upload_to='post_videos/', null=True, blank=True)
    status = models.ForeignKey(PostStatus, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the real save() method
        self.url = self.get_absolute_url()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class VotePost(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1

    VOTE_CHOICES = [
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    ]

    user = models.ForeignKey(UserPrivate, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.IntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('user', 'post')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        post_author_public = UserPublic.objects.get(user=self.post.user)
        post_author_public.rating += self.value
        post_author_public.save()


class Comment(models.Model):
    user = models.ForeignKey(UserPrivate, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CommentVote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1

    VOTE_CHOICES = [
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    ]

    user = models.ForeignKey(UserPrivate, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    value = models.IntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('user', 'comment')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        comment_author_public = UserPublic.objects.get(user=self.comment.user)
        comment_author_public.rating += self.value / 2.0  # Adding only half of the vote's value
        comment_author_public.save()


class UserNote(models.Model):
    author = models.ForeignKey(UserPrivate, on_delete=models.CASCADE, related_name='written_notes')
    user_about = models.ForeignKey(UserPrivate, on_delete=models.CASCADE, related_name='notes_about')
    note = models.TextField()

    class Meta:
        unique_together = ('author', 'user_about')

