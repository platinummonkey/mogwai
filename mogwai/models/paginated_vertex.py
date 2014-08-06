from .vertex import Vertex


def to_offset(page_num, per_page):
    """
    Convert a page_num and per_page to offset.

    :param page_num: The current page number
    :type page_num: int
    :param per_page: The maximum number of results per page
    :type per_page: int
    :rtype: int

    """
    if page_num and per_page:
        return (page_num-1) * per_page
    else:
        return None


class PaginatedVertex(Vertex):
    """
    Convenience class to easily handle pagination for traversals
    """

    @staticmethod
    def _transform_kwargs(kwargs):
        """
        Transforms paginated kwargs into limit/offset kwargs
        """
        values = kwargs.copy()
        return {
            'limit': kwargs.get('per_page'),
            'offset': to_offset(kwargs.get('page_num'), kwargs.get('per_page')),
            'types': kwargs.get('types'),
        }

    __abstract__ = True

    def outV(self, *labels, **kwargs):
        """
        :param labels: pass in the labels to follow in as positional arguments
        :param page_num: the page number to return
        :param per_page: the number of objects to return per page
        :param types: the element types this method is allowed to return
        :rtype: vertex.Vertex
        """
        return super(PaginatedVertex, self).outV(*labels, **self._transform_kwargs(kwargs))

    def outE(self, *labels, **kwargs):
        """
        :param labels: pass in the labels to follow in as positional arguments
        :param page_num: the page number to return
        :param per_page: the number of objects to return per page
        :param types: the element types this method is allowed to return
        :rtype: edge.Edge
        """
        return super(PaginatedVertex, self).outE(*labels, **self._transform_kwargs(kwargs))

    def inV(self, *labels, **kwargs):
        """
        :param labels: pass in the labels to follow in as positional arguments
        :param page_num: the page number to return
        :param per_page: the number of objects to return per page
        :param types: the element types this method is allowed to return
        :rtype: vertex.Vertex
        """
        return super(PaginatedVertex, self).inV(*labels, **self._transform_kwargs(kwargs))

    def inE(self, *labels, **kwargs):
        """
        :param labels: pass in the labels to follow in as positional arguments
        :param page_num: the page number to return
        :param per_page: the number of objects to return per page
        :param types: the element types this method is allowed to return
        :rtype: edge.Edge
        """
        return super(PaginatedVertex, self).inE(*labels, **self._transform_kwargs(kwargs))

    def bothV(self, *labels, **kwargs):
        """
        :param labels: pass in the labels to follow in as positional arguments
        :param page_num: the page number to return
        :param per_page: the number of objects to return per page
        :param types: the element types this method is allowed to return
        :rtype: list[vertex.Vertex]
        """
        return super(PaginatedVertex, self).bothV(*labels, **self._transform_kwargs(kwargs))

    def bothE(self, *labels, **kwargs):
        """
        :param labels: pass in the labels to follow in as positional arguments
        :param page_num: the page number to return
        :param per_page: the number of objects to return per page
        :param types: the element types this method is allowed to return
        :rtype: list[edge.Edge]
        """
        return super(PaginatedVertex, self).bothE(*labels, **self._transform_kwargs(kwargs))