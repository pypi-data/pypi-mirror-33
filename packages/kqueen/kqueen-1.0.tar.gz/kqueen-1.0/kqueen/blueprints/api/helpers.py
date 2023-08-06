from flask import abort
from uuid import UUID


def get_object(object_class, pk, user=None):
    # read uuid
    if isinstance(pk, UUID):
        object_id = pk
    else:
        try:
            object_id = UUID(pk, version=4)
        except ValueError:
            abort(400)

    # read namespace for user
    try:
        namespace = user.namespace
    except AttributeError:
        namespace = None

    # load object
    try:
        obj = object_class.load(namespace, object_id)
    except NameError as e:
        abort(404, repr(e))
    except Exception as e:
        abort(500, repr(e))
    return obj
