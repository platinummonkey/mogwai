
def friends_and_friends_of_friends(id, friend_edge_label) {
    /**
     * Traverse a Person and find any Friends of Friends
     *
     * :param id: Vertex id of the Person, if null abort
     * :param friend_edge_label: Edge label of the IsFriendsWith class
     * :returns: list[Person]
     */

     return g.v(id).out(friend_edge_label).loop(1){it.loops < 3}.path

}