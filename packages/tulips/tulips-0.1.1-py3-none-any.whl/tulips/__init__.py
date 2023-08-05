import importlib

from .kind import Kind


def class_for_kind(kind: str) -> Kind:
    """Return Kubernetes ResourceDefintion class.

    Args:
        kind (t.AnyStr): Resource name.

    Raises:
        ImportError: Resource is not defined.
            Example: Missing persistentvolumeclaim.py
        AttributeError: Resource has no Kind class.
            Example: Missing persistentvolumeclaim.PersistentVolumeClaim

    Returns:
        t.Callable[Kind]: Resource operator.
    """

    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(f".kind.{kind.lower()}", package=__package__)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, kind)
    return c
