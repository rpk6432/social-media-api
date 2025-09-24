import logging
from celery import shared_task
from .models import Post

logger = logging.getLogger(__name__)


@shared_task(
    bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3
)
def publish_post(self, post_id: int) -> None:
    """Celery task to publish a scheduled post."""
    updated = Post.objects.filter(id=post_id, is_published=False).update(
        is_published=True
    )

    if updated:
        logger.info(f"Post {post_id} has been published.")
    else:
        logger.warning(f"Post {post_id} not found or already published.")
