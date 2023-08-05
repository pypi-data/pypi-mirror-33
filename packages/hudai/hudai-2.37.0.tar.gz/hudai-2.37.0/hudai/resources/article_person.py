"""
hudai.resources.article_person
"""
from ..helpers.resource import Resource


class ArticlePersonResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/people')
        self.resource_name = 'ArticlePerson'

    def list(self, article_id=None, person_id=None, page=None):
        return self._list(
            article_id=article_id,
            person_id=person_id,
            page=page
        )

    def create(self, article_id, person_id):
        return self._create(
            article_id=article_id,
            person_id=person_id
        )

    def delete(self, article_id, person_id):
        return self.http_delete('/',
                                query_params={
                                    'article_id': article_id,
                                    'person_id': person_id
                                })
