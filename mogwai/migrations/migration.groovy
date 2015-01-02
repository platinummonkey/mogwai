
def find_by_migration(package_name, migration_name) {
    /**
     * Finds a particular migration by package_name and migration_name
     *
     * :param package_name: package name
     * :param migration_name: migration filename
     */
    try {
        v = g.V.has('element_type', 'mogwai_migration').has('mogwai_migration_package_name', package_name).has('mogwai_migration_migration_name', migration_name)
        assert v != null
        g.stopTransaction(SUCCESS)
        return v.next()
    } catch (err) {
        g.stopTransaction(FAILURE)
        throw(err)
    }
}