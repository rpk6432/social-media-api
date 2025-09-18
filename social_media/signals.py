import re

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, Post, User, Hashtag


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance: User, created: bool, **kwargs):
    """
    Create a Profile for each new user.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Post)
def process_post_hashtags(sender, instance: Post, created: bool, **kwargs):
    """
    Signal handler for Post model.
    Parses hashtags from the post content, creates Hashtag objects if needed,
    and attaches them to the post instance. Clears old hashtags when updating.
    """
    # Find all hashtags in the content
    hashtags = re.findall(r"#([\w-]+)", instance.content)

    # If updating an existing post, clear previous hashtags
    if not created:
        instance.hashtags.clear()

    # Create or get hashtags and attach them to the post
    for tag_name in hashtags:
        hashtag, _ = Hashtag.objects.get_or_create(name=tag_name.lower())
        instance.hashtags.add(hashtag)
