"""
hudai.resources.user_person
"""
from ..helpers.resource import Resource


class UserPersonResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users/people')
        self.resource_name = 'UserPerson'

    def list(self, user_id, page=None):
        query_params = self._set_limit_offset({'page': page})
        query_params['user_id'] = user_id

        return self.http_get('/', query_params=query_params)

    def create(self, user_id, person_id):
        return self.http_post('/', data={'person_id': person_id, 'user_id': user_id})

    def fetch(self, user_id, person_id):
        return self.http_get('/{person_id}',
                             query_params={'user_id': user_id},
                             params={'person_id': person_id})

    def delete(self, user_id, person_id):
        return self.http_delete('/{person_id}',
                                query_params={'user_id': user_id},
                                params={'person_id': person_id})
