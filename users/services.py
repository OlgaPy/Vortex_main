import logging

from users.models import UserPublic

logger = logging.getLogger(__name__)


def activate_user_account(user: UserPublic) -> UserPublic:
    """Activate user account."""
    # FIXME: need to add check if user has been banned and raise an error if it has.
    logger.info("Activating user %s", user)
    if user.is_active:
        logger.info("User %s already active", user)
        return user
    user.is_active = True
    user.save()
    return user


def deactivate_user_account(user: UserPublic) -> UserPublic:
    """Deactivate user account."""
    logger.info("Activating user %s", user)
    if not user.is_active:
        logger.info("User %s already inactive", user)
        return user
    user.is_active = False
    user.save()
    return user
