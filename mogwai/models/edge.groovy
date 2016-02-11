
def _save_edge(eid, outV, inV, elabel, attrs, exclusive) {
	/**
	 * Saves an edge between two vertices
	 * MAY NEED TO REWRITE THIS FUNCTION
	 * :param id: edge id, if null, a new vertex is created
	 * :param inV: edge inv id
	 * :param outV: edge outv id
	 * :param attrs: map of parameters to set on the edge
	 * :param exclusive: if true, this will check for an existing edge of the same label and modify it, instead of creating another edge
	 */
	try{
	  if (eid == null) {
			source = g.V(outV).next()
			target = g.V(inV).next()
			if (exclusive) {
				existing = g.V(source).outE(elabel).filter(inV().is(target))
				if(existing.size()) {
					e = existing.first()
				}
			} else {
				e = source.addEdge(elabel, target)
			}
		} else {
			e = g.E(eid).next()
		}
		for (item in attrs.entrySet()) {
      if (item.value == null) {
        e.property(item.key).remove()
      } else {
        e.property(item.key, item.value)
      }
		}
		graph.tx().commit()
		return g.E(e.id()).next()
	} catch (err) {
		graph.tx().rollback()
		throw(err)
	}
}


def _delete_edge(eid) {
    /**
     * Deletes an edge
     *
     * :param id: edge id
     */
     try {
        def e = g.E(eid).next()
        if (e != null) {
        	e.remove()
        }
        g.tx().commit()
     } catch (err) {
        g.tx().rollback()
        throw(err)
     }
}

def _get_edges_between(out_v, in_v, label, page_num, per_page) {
    try {
        def results = g.v(out_v).outE(label).as('e').inV().retain([g.v(in_v)]).back('e')
        if (page_num != null && per_page != null) {
            def start = (page_num - 1) * per_page
            def end = start + per_page
            return results[start..<end]
        } else {
            return results
        }
    } catch(err) {
        g.stopTransaction(FAILURE)
        throw(err)
    }
}

def _find_edge_by_value(value_type, label, field, value) {
    try {
       if (value_type) {
           return g.E("label", label).filter{it[field] == value}.toList()
       } else {
           return g.E("label", label).has(field, value).toList()
       }
    } catch (err) {
        g.stopTransaction(FAILURE)
        raise(err)
    }
}
