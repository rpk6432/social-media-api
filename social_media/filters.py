from django_filters import rest_framework as filters

from social_media.models import Post


class PostFilter(filters.FilterSet):
    """
    Custom filterset for the Post model.
    Allows filtering posts by hashtag name.
    """

    hashtag = filters.CharFilter(
        field_name="hashtags__name", lookup_expr="iexact"
    )

    class Meta:
        model = Post
        fields = ["hashtag"]
