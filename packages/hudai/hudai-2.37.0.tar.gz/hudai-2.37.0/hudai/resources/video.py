"""
hudai.resources.video
"""
from ..helpers.resource import Resource


class VideoResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/videos')
        self.resource_name = 'Video'

    def search(self,
             max_importance=None,
             min_importance=None,
             person_id=None,
             company_id=None,
             source_id=None,
             published_after=None,
             published_before=None,
             created_after=None,
             created_before=None,
             video_group_id=None,
             page=None):
        return self.http_get('/search',
            query_params={
                'max_importance': max_importance,
                'min_importance': min_importance,
                'person_id': person_id,
                'company_id': company_id,
                'source_id': source_id,
                'published_after': published_after,
                'published_before': published_before,
                'created_after': created_after,
                'created_before': created_before,
                'video_group_id': video_group_id,
                'page': page,
            }
        )

    def list(self,
             importance_score_min=None,
             person_id=None,
             company_id=None,
             source_id=None,
             published_after=None,
             published_before=None,
             video_group_id=None,
             page=None):
        return self._list(
            importance_score_min=importance_score_min,
            person_id=person_id,
            company_id=company_id,
            source_id=source_id,
            published_after=published_after,
            published_before=published_before,
            video_group_id=video_group_id,
            page=page
        )

    def create(self,
               title=None,
               description=None,
               transcript=None,
               poster_url=None,
               video_url=None,
               importance_score=None,
               published_at=None,
               video_group_id=None):
        return self._create(
            title=title,
            description=description,
            importance_score=importance_score,
            transcript=transcript,
            published_at=published_at,
            poster_url=poster_url,
            video_url=video_url,
            video_group_id=video_group_id
        )

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id,
               title=None,
               description=None,
               transcript=None,
               poster_url=None,
               video_url=None,
               importance_score=None,
               published_at=None,
               video_group_id=None):
        return self._update(
            entity_id,
            title=title,
            description=description,
            importance_score=importance_score,
            transcript=transcript,
            published_at=published_at,
            poster_url=poster_url,
            video_url=video_url,
            video_group_id=video_group_id
        )

    def delete(self, entity_id):
        return self._delete(entity_id)

