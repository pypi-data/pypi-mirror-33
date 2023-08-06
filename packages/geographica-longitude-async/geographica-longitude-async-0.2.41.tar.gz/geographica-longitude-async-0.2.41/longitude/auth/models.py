from longitude.models.sql import SQLCRUDModel
from longitude import config


class BaseUserModel(SQLCRUDModel):
    table_name = 'longitude_auth_user'

    _select_columns = [
        'id',
        'name',
        'username',
        'email',
        'r.id AS _role_id',
        'r.name AS _role_name',
        'r.is_superadmin AS _role_is_superadmin'
    ]

    simple_filters = (
        'username',
        'password'
    )

    _simple_joins = {
        'r': '''
            LEFT JOIN longitude_permission_role r
                ON r.id=_t.role_id
        ''',
    }

    @property
    def select_columns(self):
        return tuple(
            x
            for x
            in self._select_columns
            if (
                config.LONGITUDE_PERMISSION_PLUGIN_ENABLED or
                not x.startswith('r.')
            )
        )

    @property
    def simple_joins(self):
        joins = dict(self._simple_joins.items())

        if not config.LONGITUDE_PERMISSION_PLUGIN_ENABLED:
            joins.pop('r')

        return joins


class UserTokenModel(SQLCRUDModel):
    table_name = 'longitude_auth_user_refresh_token'

    simple_filters = (
        'auth_user_id',
    )

    async def upsert(self, values, pk=('auth_user_id',), returning_columns=None):
        return await super().upsert(values, pk=pk, returning_columns=returning_columns)

# The base user model may be overwritten if LONGITUDE_AUTH_PLUGIN_USER_MODEL
# option is set.
if config.LONGITUDE_AUTH_PLUGIN_USER_MODEL and \
    config.LONGITUDE_AUTH_PLUGIN_USER_MODEL != 'longitude.auth.models.UserModel':

    from importlib import import_module

    _cls, _module = (
        ''.join(reversed(x))
        for x
        in ''.join(reversed(config.LONGITUDE_AUTH_PLUGIN_USER_MODEL)).split('.', 1)
    )

    UserModel = getattr(import_module(_module), _cls)

else:
    class UserModel(BaseUserModel):
        pass
