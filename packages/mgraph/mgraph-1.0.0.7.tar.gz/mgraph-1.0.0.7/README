MGraph
======

A simple, object orientated graphing library.

This library provides supports to Gʀᴏᴏᴛ, and provides an uncommon feature set for graphs somewhere on the phylogenetic tree/network border.
It is written 100% in Python.
If you are looking for a pure graphing library supporting larger number of nodes you might want to check out Nᴇᴛᴡᴏʀᴋx or Iɢʀᴀᴩʜ, or for phylogenetics, Eᴛᴇ or Dᴇɴᴅʀᴏᴩʏ. 


Feature set
-----------
* Analyses:
    * Shortest path
    * Most recent common ancestor (MRCA) (DAGs)
    * Closest-relation (MRCA) (non-DAGs)
    * Path to MRCA/closest-relation
    * Find best split (acyclic graphs)
    * Find best splits (for cyclic graphs)
    * Smallest connected subgraph
    * Calculate quartet (for acyclic graphs)
    * Calculate smallest quartet (for cyclic graphs)
    * Quartet graph comparison 
    * List splits
    * Construct graph from splits
    * Consensus and supertree consensus, (basic algorithms, through Groot) 
    * Consensus, supertree consensus and phylogenetic inference (outsourced to current state of the art tools), through Groot.
    * Subgraph by predicate
* IO:
    * Newick
    * CSV
    * HTML: Vis.JS, Cytoscape.JS, SVG
    * SVG 
    * Ete
    * ASCII art
* Usability:
    * Object orientated
    * Well documented
    * Written with IDEs in mind -
        * methods include full parameter details and PEP484 annotations 

Installation
------------

```bash
(sudo) pip install mgraph
```

Usage
-----

MGʀᴀᴩʜ follows an object orientated approach, where nodes and edges are objects to which arbitrary data may (or may not) be attached.
The MGʀᴀᴩʜ library is well documented inline using [reStructuredText](http://docutils.sourceforge.net/rst.html).

```python
from mgraph import MGraph

g = MGraph.from_newick( "((A,B),C);" )
node1 = g.nodes.by_data( "A" )
node2 = g.nodes.by_data( "C" )
node3 = node1.add_child( "D" )
node3.add_edge_to( node2 )
print( g.to_csv() )
```

All edges and nodes support arbitrary Python data.

```python
from mgraph import MGraph

g = MGraph()
spam  = g.add_node( "Spam" )
beans = g.add_node( { "name": "Beans" } )
eggs  = g.add_node( 42 )
g.add_edge( spam, beans, data = {"types": ("is_parent", "is_relation"), "weight": 42 } )
```

MGraph enforces "a single way" and makes some basic constraints for cases that represent error more often than intention.

**Constraint 1.** Both nodes and edges are singular; two nodes may only share a single edge and a single edge may only span two nodes.
This doesn't mean nodes cannot have multiple relation types between them - the edge's `data` property can accommodate both.
This helps to avoid common mistakes and means that when traversing the graph all the necessary data is contained within the singular edge object and the programmer doesn't have to look anywhere else.

```python
from mgraph import MGraph

g = MGraph()
node_1 = g.add_node()
node_2 = g.add_node()

# Don't do this
g.add_edge(node_1, node_2, data = "is_parent")
g.add_edge(node_1, node_2, data = "is_relation") # Error

# Do this
g.add_edge(node_1, node_2, data = ("is_parent", "is_relation")) 
```

**Constraint 2.** Self-references are invalid.
This helps to avoid common mistakes and cycles when traversing the graph.
To represent self-references, simply attach data to the node itself. 

```python
from mgraph import MGraph

g = MGraph()
node_1 = g.add_node()

# Don't do this
g.add_edge(node_1, node_1, data = "likes_itself")  # Error

# Do this
node_1.data = "likes_itself"
```

Development
-----------

MGraph uses the unit tests run by executing the `__test__.py` file.
Code coverage should be 70% minimum for each source file.


Meta
----

```ini
host     = bitbucket,pypi
language = python3
author   = martin rusilowicz
licence  = https://www.gnu.org/licenses/agpl-3.0.html
```
