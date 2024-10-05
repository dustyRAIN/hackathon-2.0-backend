from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from contents.models import Content, Author, Tag, ContentTag
from contents.serializers import ContentSerializer, ContentPostSerializer


class ContentAPIView(APIView):

    def build_content_queryset(self, query_params):
        tag = query_params.get('tag', None)
        author_id = query_params.get('author_id', None)
        author_username = query_params.get('author_id', None)
        timeframe = query_params.get('timeframe', None)
        tag_id = query_params.get('tag_id', None)
        title = query_params.get('title', None)
        queryset = Content.objects.all()
        if timeframe:
            end_date = datetime.now()
            start_date = end_date - timedelta(timeframe)
            queryset = queryset.filter(
                timestamp__range=(start_date, end_date)
            )
        if tag_id:
            content_tags = Tag.objects.filter(id=tag_id).contenttag_set.all()
            content_ids = []
            for content_tag in content_tags:
                content_ids.append(content_tag.content.id)
            queryset = queryset.filter(id__in=content_ids)
        if tag:
            content_tags = Tag.objects.filter(
                name=tag
            ).contenttag_set.all()
            content_ids = []
            for content_tag in content_tags:
                content_ids.append(content_tag.content.id)
            queryset = queryset.filter(id__in=content_ids)
        if author_id:
            author_contents = Author.objects.filter(id=author_id).contenttag_set.all()
            content_ids = []
            for author_content in author_contents:
                content_ids.append(author_content.content.id)
            queryset = queryset.filter(id__in=content_ids)
        if author_username:
            author_contents = Author.objects.filter(
                username=author_username
            ).contenttag_set.all()
            content_ids = []
            for author_content in author_contents:
                content_ids.append(author_content.content.id)
            queryset = queryset.filter(id__in=content_ids)
        if title:
            queryset = queryset.filter(
                title__icontains=title
            )
        queryset = queryset.order_by("-id")


    def get(self, request):
        query_params = request.query_params.dict()
        queryset = self.build_content_queryset(query_params)
        serialized = ContentSerializer(queryset, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, ):
        serializer = ContentPostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        
        return Response({"error": "invalid data"}, status=400)


class ContentStatsAPIView(APIView):
    def get(self, request):
        query_params = request.query_params.dict()
        queryset = self.build_content_queryset(query_params)
        data = {
            "total_likes": 0,
            "total_shares": 0,
            "total_views": 0,
            "total_comments": 0,
            "total_engagement": 0,
            "total_engagement_rate": 0,
            "total_contents": 0,
            "total_followers": 0,
        }
        for query in queryset:
            data["total_likes"] += query.like_count
            data["total_shares"] += query.share_count
            data["total_comments"] += query.comment_count
            data["total_views"] += query.view_count
            data["total_engagement"] += data["total_likes"] + data["total_shares"] + data["total_comments"]
            data["total_followers"] += query.author.followers
            data["total_contents"] += 1

        return Response(data, status=status.HTTP_201_CREATED)
