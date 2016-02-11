
def get_maps(vid) {
    /**
     * returns the given vertex nested in a map
     */
    v = g.V(vid).next()
    [vertex:v, number:5]
}

def get_list(vid) {
    /**
     * returns the given vertex nested in a list
     */
    v = g.V(vid).next()
    [null, 0, 1, [2, v, 3], 5]
}
