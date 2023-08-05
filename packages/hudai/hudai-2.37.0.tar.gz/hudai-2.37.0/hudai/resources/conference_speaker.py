"""
hudai.resources.conference_speaker
"""
from ..helpers.resource import Resource


class ConferenceSpeakerResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/people/conferences/speakers')
        self.resource_name = 'ConferenceSpeaker'

    def list(self, conference_id, page=None):
        query_params = self._set_limit_offset({'page': page})

        return self.http_get('/', params={'conference_id': conference_id},
                                  query_params=query_params)

    def create(self, conference_id, person_id):
        return self.http_post('/', data={'person_id': person_id, 'conference_id': conference_id})

    def fetch(self, entity_id):
        return self.http_get('/{id}',
                             params={'id': entity_id})

    def delete(self, entity_id):
        return self.http_delete('/{id}',
                                params={'id': entity_id})
