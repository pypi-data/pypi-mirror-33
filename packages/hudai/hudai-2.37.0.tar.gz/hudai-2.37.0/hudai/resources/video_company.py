"""
hudai.resources.video_company
"""
from ..helpers.resource import Resource


class VideoCompanyResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/videos/companies')
        self.resource_name = 'VideoCompany'

    def list(self, video_id=None, company_id=None, page=None):
        return self._list(
            video_id=video_id,
            company_id=company_id,
            page=page
        )

    def create(self, video_id, company_id):
        return self._create(
            video_id=video_id,
            company_id=company_id
        )

    def delete(self, video_id, company_id):
        return self.http_delete('/',
                                query_params={
                                    'video_id': video_id,
                                    'company_id': company_id
                                })
