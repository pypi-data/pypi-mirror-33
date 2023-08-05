from longitude.models.sql import SQLCRUDModel


class UserModel(SQLCRUDModel):
    table_name = 'longitude_auth_users'

    select_columns = (
        'id',
        'name',
        'username',
        'email',
    )

    simple_filters = (
        'username',
        'password'
    )


class UserTokenModel(SQLCRUDModel):
    table_name = 'longitude_auth_users_refresh_tokens'

    simple_filters = (
        'auth_user_id',
    )

    async def upsert(self, values, pk=('auth_user_id',), returning_columns=None):
        return await super().upsert(values, pk=pk, returning_columns=returning_columns)
