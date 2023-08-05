from ..helpers.resource import Resource


class FeedResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users/feed')
        self.resource_name = 'Feed'

    def list(
        self,
        user_id,
        company_ids=None,
        key_terms=None,
        max_importance=None,
        max_relevance=None,
        min_importance=None,
        min_relevance=None,
        published_after=None,
        published_before=None,
        scored_after=None,
        scored_before=None,
        source_ids=None,
        tags=None,
        text=None,
        types=None,
        weights=None,
        page=None
    ):
        return self._list(
            user_id=user_id,
            company_ids=company_ids,
            key_terms=key_terms,
            max_importance=max_importance,
            max_relevance=max_relevance,
            min_importance=min_importance,
            min_relevance=min_relevance,
            published_after=published_after,
            published_before=published_before,
            scored_after=scored_after,
            scored_before=scored_before,
            source_ids=source_ids,
            tags=tags,
            text=text,
            types=types,
            weights=weights,
            page=page
        )
