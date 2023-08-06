from utility.functions import get_uuid1

def generic_factory(model_class, **kwargs):
    """
    Creates and returns a new instance with an automatically generated id
    """
    return model_class(id=get_uuid1(), **kwargs)
