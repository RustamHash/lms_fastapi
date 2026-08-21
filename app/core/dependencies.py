"""Deprecated: используйте app.api.deps вместо этого файла."""

from app.api.deps import (  # noqa: F401
    CurrentUser,
    PaginationParams,
    SessionDep,
    UserDep,
    get_current_user,
    get_current_user_id,
    get_session,
    oauth2_scheme,
    require_group,
    require_permission,
)
