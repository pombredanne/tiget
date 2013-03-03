from tiget.git.models import get_model


def model_type(model_name):
    try:
        model = get_model(model_name)
    except KeyError:
        raise TypeError
    return model


def dict_type(arg):
    try:
        key, value = arg.split('=', 1)
    except ValueError:
        raise TypeError('"=" not found in "{}"'.format(arg))
    return (key, value)
