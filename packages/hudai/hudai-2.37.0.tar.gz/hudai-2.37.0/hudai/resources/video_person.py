"""
hudai.resources.video_person
"""
from ..helpers.resource import Resource


class VideoPersonResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/videos/people')
        self.resource_name = 'VideoPerson'

    def list(self, video_id=None, person_id=None, page=None):
        return self._list(
            video_id=video_id,
            person_id=person_id,
            page=page
        )

    def create(self, video_id, person_id):
        return self._create(
            video_id=video_id,
            person_id=person_id
        )

    def delete(self, video_id, person_id):
        return self.http_delete('/',
                                query_params={
                                    'video_id': video_id,
                                    'person_id': person_id
                                })
