"""
hudai.resources.conference
"""
from ..helpers.resource import Resource


class ConferenceResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/people/conferences')
        self.resource_name = 'Conference'

    def list(self, name=None, person_id=None, before=None, after=None, company_id=None, page=None):
        return self._list(name=name,
                          person_id=person_id,
                          before=before,
                          after=after,
                          company_id=company_id,
                          page=page)

    def create(self, name=None, description=None, startsAt=None, endsAt=None, timezone=None, url=None):
        return self._create(name=name, description=description, startsAt=startsAt, endsAt=endsAt, timezone=timezone, url=url)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id, name=None, description=None, startsAt=None, endsAt=None, timezone=None):
        return self._update(entity_id, name=name, description=description, startsAt=startsAt, endsAt=endsAt, timezone=timezone)

    def delete(self, entity_id):
        return self._delete(entity_id)
