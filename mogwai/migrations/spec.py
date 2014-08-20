from __future__ import unicode_literals
from six import print_
import json

from mogwai.connection import generate_spec, execute_query


def get_existing_indices():
    """ Find all Vertex and Edge types available in the database """
    vertex_indices = execute_query('g.getIndexedKeys(Vertex.class)')
    edge_indices = execute_query('g.getIndexedKeys(Edge.class)')
    return vertex_indices, edge_indices


def write_diff_indices_to_file(filename, spec=None):  # pragma: no cover
    """ Preview of index diff specification to write to file

    :param filename: The file to write to
    :type filename: basestring
    """
    if not spec:
        print_("Generating Specification...")
        spec = generate_spec()
    print_("Writing Compiled Diff Indices to File %s ..." % filename)
    vertex_indices, edge_indices = get_existing_indices()
    with open(filename, 'wb') as f:
        for s in spec:
            for pn, pv in s['properties'].items():
                if s['element_type'] == 'Edge' and pn not in edge_indices:
                    f.writelines([pv['compiled'], ])
                elif s['element_type'] == 'Vertex' and pn not in vertex_indices:
                    f.writeliness([json.dumps(pv['compiled']), ])


def write_compiled_indices_to_file(filename, spec=None):  # pragma: no cover
    """ Write the compile index specification to file

    :param filename: The file to write to
    :type filename: basestring
    """
    if not spec:
        print_("Generating Specification...")
        spec = generate_spec()
    print_("Writing Compiled Indices to File %s ..." % filename)
    with open(filename, 'wb') as f:
        for s in spec:
            for pn, pv in s['properties'].items():
                f.writelines([json.dumps(pv['compiled']), ])


def write_specs_to_file(filename):  # pragma: no cover
    """ Generate and write a specification to file

    :param filename: The file to write to
    :type filename: basestring
    """
    print_("Generating Specification...")
    spec = generate_spec()
    print_("Writing Specification to File %s ..." % filename)
    with open(filename, 'wb') as f:
        json.dump(spec, f)
    write_compiled_indices_to_file(filename+'.idx', spec=spec)
    write_compiled_indices_to_file(filename+'.idxdiff', spec=spec)