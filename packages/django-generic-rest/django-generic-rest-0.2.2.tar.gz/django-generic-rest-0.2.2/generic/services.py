from django.contrib.auth.hashers import make_password

def generic_retrieve_single_service(repository):
    """
    Returns an instance by user and pk
    """
    def _retrieve(pk, user):
        instance = repository.get_by_id(pk, user)
        return instance

    return _retrieve

def generic_retrieve_all_service(repository):
    """
    Returns all stored instances
    """
    def _retrieve(user):
        instances = repository.get_all(user)
        return instances

    return _retrieve

def generic_delete_service(repository):
    """
    Deletes an instance by pk
    """
    def _delete(pk, user):
        instance = repository.get_by_id(pk, user)
        repository.delete_by_id(pk, user)
        return instance

    return _delete

def generic_update_service(repository, validator):
    """
    Updates an existing instance
    """
    def _update(pk, user, **kwargs):
        instance = repository.get_by_user_and_id(pk, user)
        for key, value in kwargs.items():
            instance[key] = value
        validator(instance)

        if hasattr(repository.model_class, 'password'):
            instance.password = make_password(instance.password)

        repository.persist(instance)
        return instance

    return _update
    
def generic_create_service(repository, validator, factory):
    """
    Returns and persists a new instance
    """
    def _create(user, **kwargs):
        if hasattr(repository.model_class, 'owner'):
            kwargs['owner'] = user
        
        instance = factory(repository.model_class, **kwargs)
        validator(instance)
        
        if hasattr(repository.model_class, 'password'):
            instance.password = make_password(instance.password)

        repository.persist(instance)
        return instance

    return _create
