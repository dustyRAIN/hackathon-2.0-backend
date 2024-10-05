from rest_framework import serializers

from contents.models import Content, Author, Tag, ContentTag


# For Reading the data from the DB
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'name',
            'description',
        ]


class ContentBaseSerializer(serializers.ModelSerializer):
    total_engagement = serializers.IntegerField(read_only=True)
    engagement_rate = serializers.DecimalField(read_only=True, max_digits=8, decimal_places=2)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = [
            'author',
            'unique_id',
            'url',
            'title',
            'like_count',
            'comment_count',
            'view_count',
            'share_count',
            'thumbnail_url',
            'timestamp',
            'tags',

            'total_engagement',
            'engagement_rate',
        ]

    def get_total_engagement(self, obj):
        return obj.like_count + obj.comment_count + obj.share_count
    
    def get_engagement_rate(self, obj):
        if obj.view_count > 0:
            return (obj.like_count + obj.comment_count + obj.share_count) / obj.view_count
        return 0


class ContentSerializer(serializers.Serializer):
    content = ContentBaseSerializer(read_only=True)
    author = AuthorSerializer(source=content, read_only=True)

    def get_aurhor(self, obj):
        return obj.author


class AuthorPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'username',
            'name',
            'url',
            'title',
            'big_metadata',
            'secret_value',
        ]


class ContentPostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = Content
        fields = [
            'author',
            'title',
            'big_metadata',
            'secret_value',
            'thumbnail_url',
            'like_count',
            'comment_count',
            'share_count',
            'view_count',
            'tags',
        ]

    def create(self, validated_data):
        author_data = self.context['request'].data.get('author')
        if author_data:
            try:
                author = Author.objects.get(username=author['username'])
            except Author.DoesNotExist:
                serialized_data = AuthorSerializer(**author_data)
                if serialized_data.is_valid(raise_exception=True):
                    author = serialized_data.save()
        tag_set = self.context['request'].data.get('tags')
        content = super().create(validated_data)
        if author:
            content.author = author
        if tag_set:
            for tag_name in tag_set:
                tag = Tag.objects.filter(
                    name=tag_name
                )
                if tag:
                    content_tag = ContentTag.objects.create()
                    content_tag.tag = tag
                    content_tag.content = content
        return content

    def get_tags(self, obj):
        return obj.tags_set.all()
