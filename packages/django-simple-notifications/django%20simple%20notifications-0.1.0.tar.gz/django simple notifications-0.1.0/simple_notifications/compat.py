import django

def is_user_authenticated(user):
    """
    Function for compatibility of django versions greater and equal than 2
    """
    if not callable(user.is_authenticated):
        return user.is_authenticated
    return user.is_authenticated()
