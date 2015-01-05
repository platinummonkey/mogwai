
class MockVertex(object):

    def __init__(self, label, props, composite_indices={}, model_class_name=''):
        self.element_type = label
        self.label = label
        self._properties = props or {}
        self.composite_indices = composite_indices or {}
        self.model_class_name = model_class_name or ''


class MockEdge(object):

    def __init__(self, label, props, composite_indices={}, model_class_name=''):
        self.label = label
        self._properties = props or {}
        self.composite_indices = composite_indices or {}
        self.model_class_name = model_class_name or ''
