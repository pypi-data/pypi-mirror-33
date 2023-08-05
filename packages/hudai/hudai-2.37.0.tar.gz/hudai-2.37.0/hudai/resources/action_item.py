"""
hudai.resources.action_item
"""
from ..helpers.resource import Resource


class ActionItemResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users/action-items')
        self.resource_name = 'ActionItem'

    def list(self, created_after=None,
                   created_before=None,
                   entity_id=None,
                   user_id=None,
                   company_ids=None,
                   person_ids=None,
                   completed=None,
                   completed_before=None,
                   completed_after=None,
                   dismissed=None,
                   dismissed_before=None,
                   dismissed_after=None,
                   archived=None,
                   archived_before=None,
                   archived_after=None,
                   page=None):
        return self._list(created_after=created_after,
                          created_before=created_before,
                          id=entity_id,
                          user_id=user_id,
                          company_ids=company_ids,
                          person_ids=person_ids,
                          completed=completed,
                          completed_before=completed_before,
                          completed_after=completed_after,
                          dismissed=dismissed,
                          dismissed_before=dismissed_before,
                          dismissed_after=dismissed_after,
                          archived=archived,
                          archived_before=archived_before,
                          archived_after=archived_after,
                          page=page)

    def create(self, user_id=None,
                     action_type=None,
                     associated_entity_type=None,
                     associated_entity_id=None,
                     completed_at=None,
                     dismissed_at=None,
                     propensity_score=None,
                     content_items=[]):
        return self._create(user_id=user_id,
                            action_type=action_type,
                            associated_entity_type=associated_entity_type,
                            associated_entity_id=associated_entity_id,
                            completed_at=completed_at,
                            dismissed_at=dismissed_at,
                            propensity_score=propensity_score,
                            content_items=content_items)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id,
                     user_id=None,
                     action_type=None,
                     associated_entity_type=None,
                     associated_entity_id=None,
                     completed_at=None,
                     dismissed_at=None,
                     archived_at=None,
                     propensity_score=None):
        return self._update(entity_id,
                            user_id=user_id,
                            action_type=action_type,
                            associated_entity_type=associated_entity_type,
                            associated_entity_id=associated_entity_id,
                            completed_at=completed_at,
                            dismissed_at=dismissed_at,
                            archived_at=archived_at,
                            propensity_score=propensity_score)

    def delete(self, entity_id):
        return self._delete(entity_id)
