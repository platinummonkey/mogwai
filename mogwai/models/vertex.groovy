
def _save_vertex(vid, vlabel, attrs) {
    /**
     * Saves a vertex
     *
     * :param id: vertex id, if null, a new vertex is created
     * :param attrs: map of parameters to set on the vertex
     */
    try {
        def v = vid == null ? graph.addVertex(label, vlabel) : g.V(vid).next()

        for (item in attrs.entrySet()) {
            if (item.value == null) {
                v.property(item.key).remove()
            } else {
                v.property(item.key, item.value)
            }
        }
        graph.tx().commit()
        return g.V(v.id()).next()
    } catch (err) {
        graph.tx().rollback()
        throw(err)
    }
}

def _delete_vertex(vid) {
    /**
     * Deletes a vertex
     *
     * :param id: vertex id
     */
     try {
        def v = g.V(vid).next()
        v.remove()
        graph.tx().commit();
     } catch (err) {
        graph.tx().rollback();
        throw(err)
     }
}

def _create_relationship(id, in_direction, edge_label, edge_attrs, vertex_attrs) {
    /*
     * Creates an vertex and edge from the given vertex
     *
     * :param id: vertex id, cannot be null
     * :param direction: direction of edge from original vertex
     * :param edge_label: label of the edge
     * :param edge_attrs: map of parameters to set on the edge
     * :param vertex_attrs: map of parameters to set on the vertex
     */
    try {
        def v1 = g.V(id).next()
        def v2 = graph.addVertex()
        def e

        for (item in vertex_attrs.entrySet()) {
                v2.property(item.key, item.value)
        }
        v2 = g.V(v2.id).next()
        if(in_direction) {
            e = graph.addEdge(v2, v1, edge_label)
        } else {
            e = graph.addEdge(v1, v2, edge_label)
        }
        for (item in edge_attrs.entrySet()) {
            e.property(item.key, item.value)
        }
        return [g.E(e.id).next(), v2)]
    } catch (err) {
        g.stopTransaction(FAILURE)
        throw(err)
    }
}

def _traversal(vid, operation, labels, start, end, element_types) {
    /**
     * performs vertex/edge traversals with optional edge labels and pagination
     * :param id: vertex id to start from
     * :param operation: the traversal operation
     * :param label: the edge label to filter on
     * :param page_num: the page number to start on (pagination begins at 1)
     * :param per_page: number of objects to return per page
     * :param element_types: list of allowed element types for results
     */
    def results = g.V(vid)
    def label_args = labels == null ? [] : labels
    switch (operation) {
        case "inV":
            results = results.in(*label_args)
            break
        case "outV":
            results = results.out(*label_args)
            break
        case "inE":
            results = results.inE(*label_args)
            break
        case "outE":
            results = results.outE(*label_args)
            break
        case "bothE":
            results = results.bothE(*label_args)
            break
        case "bothV":
            results = results.both(*label_args)
            break
        default:
            throw NamingException()
    }
    if (start != null && end != null) {
        results = results[start..<end]
    }
    if (element_types != null) {
        results = results.filter{it.get().label() in element_types}
    }
    return results
}

def _delete_related(vid, operation, lbs) {
    try{
        /**
         * deletes connected vertices / edges
         */
        def results = g.V(vid)
        def label_args = lbs == null ? [] : lbs
        switch (operation) {
            case "inV":
                results = results.in(*label_args)
                break
            case "outV":
                results = results.out(*label_args)
                break
            case "inE":
                results = results.inE().hasLabel(*label_args)
                break
            case "outE":
                results = results.outE().hasLabel(*label_args)
                break
            default:
                throw NamingException()
        }
        results.each{it.remove()}
        graph.tx().commit()
    } catch (err) {
        graph.tx().rollback()
        raise(err)
    }
}

def _find_vertex_by_value(value_type, vlabel, field, val) {
    /**
     * I'm not sure about the need for value_type
     */
    try {
       if (value_type) {
           return g.V().hasLabel(vlabel).filter{it.get().value(field) == val}
       } else {
           return g.V().hasLabel(vlabel).has(field, val)
       }
    } catch (err) {
        graph.tx().rollback()
        raise(err)
    }
}
