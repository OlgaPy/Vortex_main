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

class UserPublic(models.Model):
    user = models.OneToOneField(UserPrivate, on_delete=models.CASCADE, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    rating = models.FloatField(default=0)


class PostStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(UserPrivate, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    video = models.FileField(upload_to='post_videos/', null=True, blank=True)
    status = models.ForeignKey(PostStatus, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the real save() method
        self.url = self.get_absolute_url()


class Vote(models.Model):
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
