.. _ideas:

Ideas
=====

We'll keep a running list of ideas for future enhancements. Please note this is likely incomplete and not always
up-to-date with the issue tracker. Also these are in no-particular order.

 * **Titan 0.5.x + support --> TinkerPop3 and Gremlin3 Support**
    * Websocket support for streaming results (generators)
    * Build in pluggable gevent/eventlet support for streaming results -- mogwai operations should be asynchronous
 * **Improved Index/Constraint Specification System**
    * Create Faunus or runnable job against the database to enforce a specification
 * **Support Migrations - The `South` project lends inspiration here.**
 * **Add Relationship attribute magic**
    * Schema enforcement for Faunus
    * Creation/Traversal enforcement
 * **Integrate additional common metric collectors**
 * **Python 3 compatibility**
    * Currently not possible with gevent and pyparsing
 * **Filter lazy-evaluated gremlin query.**
    * Perhaps: MyVertexModel.query().filter(someval__lte=2)
 * **Database Export/Import functionality**
 * **Enum MetaClass optional memcache/etc support.**
 * **Gremlin Query builder**
   * Optional groovy script generator based on query.
 * **Groovy script inspections tool for optimization hints, common algorithms, possible syntax errors.**