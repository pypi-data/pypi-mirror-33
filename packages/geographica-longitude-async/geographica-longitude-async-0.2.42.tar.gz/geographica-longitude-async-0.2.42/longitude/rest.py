import json

from functools import wraps

from longitude.validators import min_value, combine_validations, max_value
from longitude.config import PAGINATION_PAGE_SIZE, PAGINATION_MAX_PAGE_SIZE
from longitude.schemas import Schema
from marshmallow import post_load
from marshmallow import fields as sch_fields


class ListEPFilterSchema(Schema):

    meta = sch_fields.Boolean(required=True, missing=True)
    results = sch_fields.Boolean(required=True, missing=True)
    page = sch_fields.Integer(required=True, missing=1, validate=min_value(1))
    page_of = sch_fields.Integer(required=True, missing=None, validate=min_value(1))

    if PAGINATION_MAX_PAGE_SIZE is not None:
        page_size = sch_fields.Integer(
            required=False,
            default=PAGINATION_PAGE_SIZE,
            validate=combine_validations(
                max_value(PAGINATION_MAX_PAGE_SIZE),
                max_value(10000),
                min_value(1)
            )
        )

    @post_load
    def add_pagination(self, out_data):

        if PAGINATION_MAX_PAGE_SIZE is None:
            out_data['page_size'] = PAGINATION_PAGE_SIZE

        return out_data


def paginated(fn):

    @wraps(fn)
    async def paginated_fn(request, *args, **kwargs):
        for key, value in ListEPFilterSchema().load(request.args)[0].items():
            request.args[key] = [value]

        res = await fn(request, *args, **kwargs)

        # We expect the user to take into account request.meta and request.results
        # However, if the user does not treat them and the payload includes results
        # /meta when they should, let's try to remove it and at least get rid
        # of the transports costs

        if res.body and res.content_type == 'application/json' and (
            (not request.args.get('meta') and b'"meta"' in res.body) or
            (not request.args.get('results') and b'"results"' in res.body)
        ):
            body = json.loads(res.body)

            if not request.args.get('meta'):
                body.pop('meta', None)

            if not request.args.get('results'):
                body.pop('results', None)

            res.body = json.dumps(body).encode()

        return res

    return paginated_fn
