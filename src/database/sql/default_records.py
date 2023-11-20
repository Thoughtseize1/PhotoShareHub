from src.database.sql.models import Permission


permissions = [
    Permission(
        role_name="User",
        can_add_image=False,
        can_update_image=False,
        can_delete_image=False,
        can_add_tag=False,
        can_update_tag=False,
        can_delete_tag=False,
        can_update_comment=False,
        can_delete_comment=False,
    ),
    Permission(
        role_name="Moderator",
        can_add_image=False,
        can_update_image=True,
        can_delete_image=True,
        can_add_tag=False,
        can_update_tag=True,
        can_delete_tag=True,
        can_update_comment=True,
        can_delete_comment=False,
    ),
    Permission(
        role_name="Admin",
        can_add_image=True,
        can_update_image=True,
        can_delete_image=True,
        can_add_tag=True,
        can_update_tag=True,
        can_delete_tag=True,
        can_update_comment=True,
        can_delete_comment=True,
    ),
]
