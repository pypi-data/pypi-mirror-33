import itertools
import warnings
from collections import defaultdict
from typing import AbstractSet, Callable, Dict, FrozenSet, Iterator, List, Set, TypeVar, Union, cast, Optional

import sys

import math
from mgraph.graphing import DEdgePredicate, DNodePredicate, DNodeToObject, EDirection, FollowParams, IsolationError, IsolationPoint, MEdge, MGraph, MNode, UEdgePredicate, UNodePredicate
from mhelper import ComponentFinder, Logger, NOT_PROVIDED, NotFoundError, ansi, array_helper, string_helper, LoopDetector, LogicError


_LOG = Logger( "isolate", False )

T = TypeVar( "T" )

MAX_GRAPH_SIZE = 1000


def count_nodes( graph: MGraph, predicate: UNodePredicate ) -> int:
    """
    Returns the number of matching nodes.
    """
    predicate = realise_node_predicate( predicate )
    return sum( 1 for x in graph.nodes if predicate( x ) )


def find_shortest_path( graph: MGraph, start: UNodePredicate, end: UNodePredicate, filter: UNodePredicate = None, direction = EDirection.BOTH ) -> List["MNode"]:
    """
    Obtains the shortest path between two nodes.
    
    :param graph:           Graph
    :param start:           Start of path 
    :param end:             End of path  
    :param filter:          Filter on nodes 
    :param direction:       Direction to follow edges 
    :return:                Path, as a list of elements from `start` to `end`.
    :except NotFoundError:  No such path exists 
    """
    start = realise_node_predicate_as_set( graph, start )
    end = realise_node_predicate( end )
    
    # If we are already at the end that is fine
    for x in start:
        if end( x ):
            return [x]
    
    open: List[List[MNode]] = [[x] for x in start]
    closed = set()
    
    filter = realise_node_predicate( filter )
    
    while open:
        cur: List[MNode] = open.pop( 0 )
        nod: MNode = cur[-1]
        closed.add( nod )
        
        for edge in nod.edges.by_direction( direction ):
            oth = edge.opposite( nod )
            
            if end( oth ):
                return cur + [oth]
            
            if oth not in closed and filter( oth ):
                open.append( cur + [oth] )
    
    raise NotFoundError( "There is no «{}» path between nodes «{}» and «{}» using the filter «{}».".format( direction, start, end, filter ) )


def find_common_ancestor( graph: MGraph,
                          query: UNodePredicate,
                          *,
                          filter: UNodePredicate = None,
                          direction: EDirection = EDirection.INCOMING,
                          default = NOT_PROVIDED ) -> "MNode":
    """
    Convenience function that returns the MRCA from `find_common_ancestor_paths`.
    """
    try:
        p = find_common_ancestor_paths( graph, query, filter = filter, direction = direction )
    except NotFoundError:
        if default is not NOT_PROVIDED:
            return default
        else:
            raise
    
    return p[0][0]


class NodePath:
    def __init__( self, end: MNode, paths: Dict[MNode, MNode] ):
        self.end = end
        self.__paths = paths
        self.__path = None
    
    
    @property
    def node( self ):
        return self.end
    
    
    @property
    def visited( self ):
        return self.__path.keys()
    
    
    @property
    def path( self ):
        if self.__path is None:
            r = []
            e = self.end
            
            while e:
                r.append( e )
                e = self.__paths[e]
            
            self.__path = list( reversed( r ) )
        
        return self.__path


class BfsState:
    """
    :ivar node:        Node this state represents 
    """
    
    
    def __init__( self, node: MNode, parent: Optional["BfsState"], is_reentry: bool, distance: int ) -> None:
        """
        CONSTRUCTOR
        """
        self.node: MNode = node
        self.parent: Optional[BfsState] = parent
        self.is_reentry = is_reentry
        self.distance = distance
    
    
    def __repr__( self ):
        return "State{{{}{} | ({})}}".format( "REENTRY " if self.is_reentry else "", self.node, self.parent.node if self.parent else "0" )


def iter_depth_first(
        graph: MGraph,
        start: UNodePredicate,
        filter: UNodePredicate = None,
        direction: EDirection = EDirection.BOTH,
        sort = None ):
    start = realise_node_predicate_as_set( graph, start )
    filter = realise_node_predicate( filter )
    open: List[BfsState] = [BfsState( x, None, False, 0 ) for x in start]  # stack
    closed = set()
    safe_loop = LoopDetector( limit = MAX_GRAPH_SIZE, info = { "closed": closed } )
    
    while safe_loop( open ):
        v = open.pop( -1 )
        
        if v.node in closed:
            continue
        
        yield v
        closed.add( v.node )
        
        rels = v.node.get_relations( direction )
        
        if sort is not None:
            rels = reversed( sorted( rels, key = sort ) )
        
        for rel in rels:
            if not filter( rel ):
                continue
            
            rel_state = BfsState( rel, v, False, v.distance + 1 )
            open.append( rel_state )


def iter_breadth_first(
        graph: MGraph,
        start: UNodePredicate,
        filter: UNodePredicate = None,
        direction: EDirection = EDirection.BOTH,
        yield_reentry: bool = False,
        closed: Dict[MNode, BfsState] = None ):
    start = realise_node_predicate_as_set( graph, start )
    filter = realise_node_predicate( filter )
    open: List[BfsState] = [BfsState( x, None, False, 0 ) for x in start]
    closed = closed if closed is not None else { }
    
    closed.clear()
    closed.update( { x.node: x for x in open } )
    safe_loop = LoopDetector( limit = MAX_GRAPH_SIZE, info = { "closed": closed } )
    yield from open
    
    while safe_loop( open ):
        state = open.pop( 0 )
        
        # Iterate the relations
        for rel in state.node.get_relations( direction ):
            if not filter( rel ):
                continue
            
            rel_state = closed.get( rel )
            
            if rel_state is not None:
                if yield_reentry:
                    yield BfsState( rel, state, True, state.distance + 1 )
                continue
            
            rel_state = BfsState( rel, state, False, state.distance + 1 )
            closed[rel] = rel_state
            yield rel_state
            open.append( rel_state )


def find_common_ancestor_paths( graph: MGraph,
                                query: UNodePredicate,
                                *,
                                filter: UNodePredicate = None,
                                direction: EDirection = EDirection.INCOMING
                                ) -> List[List["MNode"]]:
    """
    Finds the most recent common ancestor of the nodes predicated by the specified filter.
        
    :param graph:       Target graph.
    :param query:       Predicate determining the origin nodes.
    :param filter:      Predicate over which to nodes may be traversed.
    :param direction:   Direction over which nodes may be traversed.
                            INCOMING  = Against edges
                                        This is the default, it finds the MRCA on a rooted graph
                            BOTH      = Edge independent
                                        This finds the shortest path between the origins
                            OUTGOING  = With edges
                                        I don't know why you'd use this
    :return: A list of lists, each list has the MRCA as the first element, and the subsequent elements
             of that list describing the path from the MRCA to the `query` nodes.
             
    :except ValueError: Filter excludes all nodes
    :except NotFoundError: Nodes do not share an MRCA 
    """
    
    origins = realise_node_predicate_as_set( graph, query )
    
    if len( origins ) == 1:
        return [list( origins )]
    
    if not origins:
        raise ValueError( "The specified filter («{}») excludes all nodes in the graph («{}»).".format( filter, graph.to_compact() ) )
    
    num_origins = len( origins )
    closed_lists = [{ } for _ in origins]
    generators = [iter_breadth_first( graph, node, filter, direction, closed = closed_lists[index] ) for index, node in enumerate( origins )]
    loop_detector = LoopDetector( MAX_GRAPH_SIZE, info = { "closed_lists": closed_lists } )
    
    node_touch_sets: Dict[MNode, Set[int]] = { }
    
    loop = True
    mrca = None
    
    while loop:
        loop_detector()
        loop = False
        
        for origin_index, generator in enumerate( generators ):
            try:
                state: BfsState = next( generator )
                assert state.node in closed_lists[origin_index]
            except StopIteration:
                continue
            
            loop = True
            
            node_touch_set = node_touch_sets.get( state.node )
            
            if node_touch_set is None:
                node_touch_set = { origin_index }
                node_touch_sets[state.node] = node_touch_set
            elif origin_index not in node_touch_set:
                node_touch_set.add( origin_index )
                
                if len( node_touch_set ) == num_origins:
                    mrca = state.node
                    loop = False
                    break
            else:
                raise LogicError( "node_touch_sets recursed on {}. I have already seen this node before and didn't expect to see it again because I didn't specify `iter_breadth_first::yield_reentry`.".format( state.node ) )
    
    if mrca is None:
        raise NotFoundError( "The nodes («{}») do not share a common ancestor in the graph.".format( string_helper.format_array( origins ) ) )
    
    results: List[List[MNode]] = []
    
    for origin_index in range( num_origins ):
        closed_list = closed_lists[origin_index]
        
        origin_path: List[MNode] = []
        rewind_node: BfsState = closed_list[mrca]
        loop_detector = LoopDetector( limit = MAX_GRAPH_SIZE, info = { "path": origin_path } )
        
        while rewind_node:
            loop_detector()
            origin_path.append( rewind_node.node )
            rewind_node = closed_list[rewind_node.parent.node] if rewind_node.parent is not None else None
        
        results.append( origin_path )
    
    return results


def find_isolation_point( graph: MGraph, is_inside: UNodePredicate, is_outside: UNodePredicate ) -> IsolationPoint:
    """
    Convenience function that calls `find_isolation_points`, returning the resultant point or raising an error.
    
    :except IsolationError: Points are not isolated.
    """
    is_inside = realise_node_predicate_as_set( graph, is_inside )
    is_outside = realise_node_predicate_as_set( graph, is_outside )
    
    points = find_isolation_points( graph, is_inside, is_outside )
    
    if len( points ) != 1:
        msg = "Cannot extract an isolation point from the graph because the inside set ({}) is not isolated from the outside set ({})."
        raise IsolationError( msg.format( is_inside, is_outside ), is_inside, is_outside )
    
    return points[0]


def find_isolation_points( graph: MGraph, is_inside: UNodePredicate, is_outside: UNodePredicate ) -> List[IsolationPoint]:
    """
    Finds the points on the graph that separate the specified `inside` nodes from the `outside` nodes.
    
          --------I
      ----X1
      |   --------I
      |
    --X2
      |
      |   --------O
      ----X3
          --------O
         
    
    Nodes (X) not in the `inside` (I) and `outside` (O) sets are can be either inside or outside the isolated subgraph, however this
    algorithm will attempt to keep as many as possible outside, so in the diagram about, the point that isolates I from O is X1. 
    
    Ideally, there will just be one point in the results list, but if the inside points are scattered, more than one point will be
    returned, e.g. X1 and X3 separate I from O:
    
          --------I
      ----X1
      |   --------I
      |
    --X2
      |           --------I
      |   --------X3
      ----X4      --------I
          |
          --------O
     
     
    :param graph:         Target graph.
    :param is_outside:   A delegate expression yielding `True` for nodes outside the set to be separated, and `False` for all other nodes. 
    :param is_inside:    A delegate expression yielding `True` for nodes inside the set to be separated,  and `False` for all other nodes. 
    :return:          A list of `IsolationPoint` detailing the isolation points. 
    """
    # Iterate over all the edges to make a list of `candidate` edges
    # - those separating INSIDE from OUTSIDE
    candidates: List[IsolationPoint] = []
    
    is_inside = realise_node_predicate_as_set( graph, is_inside )
    is_outside = realise_node_predicate_as_set( graph, is_outside )
    
    if not is_inside:
        raise ValueError( "Cannot find isolation points because there are no interior nodes. Interior = {}. Exterior = {}.".format( string_helper.format_array( is_inside ), string_helper.format_array( is_outside ) ) )
    
    if not is_outside:
        raise ValueError( "Cannot find isolation points because there are no exterior nodes. Interior = {}. Exterior = {}.".format( string_helper.format_array( is_inside ), string_helper.format_array( is_outside ) ) )
    
    all_nodes = set( graph )
    
    for edge in graph.edges:
        _LOG( "~~~~ {} ~~~~", edge )
        left_nodes = set( graph.follow( FollowParams( start = edge.left, edge_filter = lambda x: x is not edge ) ).visited_nodes )
        right_nodes = all_nodes - left_nodes
        
        for node, inside_nodes, outside_nodes in ((edge.left, left_nodes, right_nodes), (edge.right, right_nodes, left_nodes)):
            _LOG( "WANT INSIDE:  {}", is_inside )
            _LOG( "WANT OUTSIDE: {}", is_outside )
            _LOG( "INSIDE:       {}", inside_nodes )
            _LOG( "OUTSIDE:      {}", outside_nodes )
            
            if not __check_inside_outside( inside_nodes, is_inside, is_outside, outside_nodes ):
                continue
            
            pure_inside_nodes = set( x for x in inside_nodes if x in is_inside )
            pure_outside_nodes = set( x for x in outside_nodes if x in is_outside )
            
            candidates.append( IsolationPoint( edge, node, edge.opposite( node ), pure_inside_nodes, pure_outside_nodes, inside_nodes, outside_nodes ) )
    
    # Our candidates overlap, so remove the redundant ones
    drop_candidates = []
    
    for candidate_1 in candidates:
        for candidate_2 in candidates:
            if candidate_1 is candidate_2:
                continue
            
            is_subset = candidate_1.pure_inside_nodes.issubset( candidate_2.pure_inside_nodes )
            
            # If the candidates encompass different sequences don't bother
            if not is_subset:
                continue
            
            # Any candidates that are a _strict_ subset of another can be dropped
            if len( candidate_1.pure_inside_nodes ) < len( candidate_2.pure_inside_nodes ):
                drop_candidates.append( candidate_1 )
                break
            
            # Any candidates equal to another, but have a greater number of cladistic nodes, can be dropped
            if len( candidate_1.all_inside_nodes ) > len( candidate_2.all_inside_nodes ):
                drop_candidates.append( candidate_1 )
                break
    
    for candidate in drop_candidates:
        candidates.remove( candidate )
    
    return candidates


def __check_inside_outside( inside_nodes: AbstractSet["MNode"],
                            is_inside: AbstractSet["MNode"],
                            is_outside: AbstractSet["MNode"],
                            outside_nodes: AbstractSet["MNode"]
                            ) -> bool:
    for x in inside_nodes:
        if x in is_outside:
            _LOG( ansi.FORE_RED + "REJECTED" + ansi.FORE_RESET + " - OUTSIDE NODE IS INSIDE: {}", x )
            return False
    
    for x in outside_nodes:
        if x in is_inside:
            _LOG( ansi.FORE_RED + "REJECTED" + ansi.FORE_RESET + " - INSIDE NODE IS OUTSIDE: {}", x )
            return False
    
    _LOG( ansi.FORE_GREEN + "ACCEPTED" + ansi.FORE_RESET )
    return True


def realise_node_predicate_as_set( graph: MGraph, node_filter: UNodePredicate ) -> AbstractSet["MNode"]:
    """
    Converts a node predicate to a set, given a graph.
    """
    if node_filter is None:
        return set( graph.nodes )
    elif isinstance( node_filter, MNode ):
        return { node_filter }
    elif isinstance( node_filter, set ) or isinstance( node_filter, frozenset ):
        return node_filter
    elif isinstance( node_filter, list ) or isinstance( node_filter, tuple ):
        return set( node_filter )
    else:
        return set( node for node in graph if node_filter( node ) )


def realise_predicate( entity_filter: Union[UEdgePredicate, UNodePredicate], type_: type ) -> Union[DEdgePredicate, DNodePredicate]:
    """
    Converts a predicate of ambiguous type to a predicate function.
    """
    if entity_filter is None:
        return lambda _: True
    elif isinstance( entity_filter, type_ ):
        return (lambda y: lambda x: x is y)( entity_filter )
    elif isinstance( entity_filter, set ):
        return (lambda y: lambda x: x in y)( entity_filter )
    elif isinstance( entity_filter, list ) or isinstance( entity_filter, tuple ):
        return (lambda y: lambda x: x in y)( set( entity_filter ) )
    else:
        return entity_filter


def realise_edge_predicate( edge_filter: UEdgePredicate ) -> DEdgePredicate:
    """
    Converts a predicate of ambiguous type to a function.
    """
    return realise_predicate( edge_filter, MEdge )


def realise_node_predicate( node_filter: UNodePredicate ) -> DNodePredicate:
    """
    Converts a predicate of ambiguous type to a function.
    :return: 
    """
    return realise_predicate( node_filter, MNode )


def find_connected_components( graph: MGraph ) -> List[List["MNode"]]:
    """
    Calculates and returns the list of connected components.
    """
    cf = ComponentFinder()
    
    for edge in graph.edges:
        cf.join( edge.left, edge.right )
    
    return cast( List[List["MNode"]], cf.tabulate() )


def get_intermediaries( graph: MGraph, node_filter: UNodePredicate ) -> Set[MNode]:
    """
    By calculating the shortest paths between all pairs of nodes in the provided set,
    this function returns all the nodes required to form their complete subgraph. 
    :param graph:           Source graph
    :param node_filter:     Filter  
    :return: 
    """
    nodes = realise_node_predicate_as_set( graph, node_filter )
    
    results = set()
    
    for a, b in array_helper.lagged_iterate( nodes ):
        results.update( find_shortest_path( graph, a, b ) )
    
    return results


class AbstractQuartet:
    def __init__( self, a, b, c, d ):
        self.__nodes = frozenset( { a, b, c, d } )
    
    
    @property
    def nodes( self ) -> FrozenSet[MNode]:
        return self.__nodes
    
    
    def get_unsorted_key( self, key: Callable[[MNode], T] = None ) -> FrozenSet[T]:
        if key is None:
            key = cast( Callable[[MNode], T], MNode.data.fget )
        
        r = frozenset( key( x ) for x in self.__nodes )
        
        if len( r ) != 4:
            raise ValueError( "Key allows two nodes in the same quartet to be considered equivalent." )
        
        return r


class BadQuartet( AbstractQuartet ):
    """
    Represents something that we couldn't determine the quartet status of.
    (This class is essentially a frozenset in a named class)
    """
    
    
    def __str__( self ):
        return "Bad({} ; {} ; {} ; {})".format( *self.nodes )


class Quartet( AbstractQuartet ):
    """
    Represents a quartet.
    
         A          C 
          \        /
           --------
          /        \
         B          D  
    """
    
    
    def __init__( self, a, b, c, d ):
        super().__init__( a, b, c, d )
        self.__left_nodes = frozenset( { a, b } )
        self.__right_nodes = frozenset( { c, d } )
    
    
    def __str__( self ):
        return "{} + {} | {} + {}".format( *self.__left_nodes, *self.__right_nodes )
    
    
    @property
    def left_nodes( self ) -> FrozenSet[MNode]:
        return self.__left_nodes
    
    
    @property
    def right_nodes( self ) -> FrozenSet[MNode]:
        return self.__right_nodes
    
    
    def get_sorted_key( self, key: Callable[[MNode], T] = None ) -> FrozenSet[FrozenSet[T]]:
        if key is None:
            key = cast( Callable[[MNode], T], MNode.data.fget )
        
        l = frozenset( key( x ) for x in self.__left_nodes )
        r = frozenset( key( x ) for x in self.__right_nodes )
        
        if len( l ) != 2 or len( r ) != 2:
            raise ValueError( "Key allows two nodes in the same quartet to be considered equivalent." )
        
        return frozenset( { l, r } )


class DistanceMatrix:
    def __init__( self, graph: MGraph, node_filter: UNodePredicate ):
        self.nodes = realise_node_predicate_as_set( graph, node_filter )
        self.data = { }
        
        for a, b in array_helper.lagged_iterate( self.nodes ):
            sp = find_shortest_path( graph, a, b )
            self.data[a, b] = len( sp )
    
    
    def __setitem__( self, key, value ):
        a, b = sorted( key, key = id )
        self.data[a, b] = value
    
    
    def __getitem__( self, key ):
        a, b = sorted( key, key = id )
        return self.data[a, b]


def get_distance_matrix( graph: MGraph, node_filter: UNodePredicate ) -> DistanceMatrix:
    """
    Gets the distance matrix between nodes.
    """
    return DistanceMatrix( graph, node_filter )


class QuartetComparison:
    def __init__( self, missing_in_right: "QuartetCollection", missing_in_left: "QuartetCollection", match: "QuartetCollection", mismatch: "QuartetCollection", all: "QuartetCollection" ):
        """
        CONSTRUCTOR
        :param missing_in_right:    Quartets in the right ("other") that are not in the left ("self") 
        :param missing_in_left:     Quartets in the left ("self") that are not in the right ("other")
        :param match:               Quartets present in both, which have the same node positions. 
        :param mismatch:            Quartets present in both, which have different node positions. 
        """
        self.missing_in_right = missing_in_right
        self.missing_in_left = missing_in_left
        self.match = match
        self.mismatch = mismatch
        self.all = all
        assert len( all ) == (len( missing_in_right ) + len( missing_in_left ) + len( match ) + len( mismatch ))
    
    
    def __len__( self ):
        return len( self.missing_in_right ) + len( self.missing_in_left ) + len( self.match ) + len( self.mismatch )


class QuartetCollection:
    """
    Manages a collection of quartets.
    """
    
    
    def __init__( self, quartets ):
        self.__by_node: Dict[FrozenSet[MNode], AbstractQuartet] = { }
        
        for quartet in quartets:
            self.__by_node[quartet.nodes] = quartet
    
    
    def __str__( self ):
        return "QuartetCollection(({}))".format( string_helper.format_array( self ) )
    
    
    def __len__( self ) -> int:
        return len( self.__by_node )
    
    
    def __bool__( self ):
        return len( self ) != 0
    
    
    def __iter__( self ) -> Iterator[AbstractQuartet]:
        return iter( self.__by_node.values() )
    
    
    def by_key( self, *args ) -> AbstractQuartet:
        if len( args ) > 1:
            return self.__by_node[frozenset( args )]
        else:
            return self.__by_node[args[0]]
    
    
    def by_node( self, *args ) -> AbstractQuartet:
        if len( args ) > 1:
            return self.__by_node[frozenset( args )]
        else:
            return self.__by_node[args[0]]
    
    
    def get_unsorted_lookup( self, key: Callable[[MNode], T] = None, no_bad: bool = False ) -> Dict[FrozenSet[T], AbstractQuartet]:
        """
        Creates a new collection using a different key (equality comparison) for the Quartets.
        """
        if key is None:
            key = MNode.data.fget
        
        r = { }
        
        for quartet in self:
            if no_bad and not isinstance( quartet, BadQuartet ):
                continue
            
            r[quartet.get_unsorted_key( key )] = quartet
        
        if len( r ) != len( self ):
            raise ValueError( "Key allows two nodes in the same quartet collection to be considered equivalent." )
        
        return r
    
    
    def compare( self, other: "QuartetCollection", key: Callable[[MNode], T] = None ) -> QuartetComparison:
        """
        Compares two QuartetCollection's.
        :param other:   `QuartetCollection` to compare with 
        :param key:     How to determine node equality.
                        If no key is provided, the key used when calling `get_quartets` is used.
                        Avoid using keys that allow two nodes in the same graph to be considered equivalent.
                        The default key is `MNode.data`.
        :return:        A `QuartetComparison` object. The quartet instances from `self` are used preferentially (where available).  
        """
        if key is None:
            key = MNode.data.fget
        
        lookup = other.get_unsorted_lookup( key )
        
        no_equiv = []
        match = []
        mismatch = []
        
        for quartet in self:
            quartet_key = quartet.get_unsorted_key( key )
            equiv = lookup.pop( quartet_key, None )
            
            if equiv is None:
                no_equiv.append( quartet )
                continue
            
            if isinstance( quartet, BadQuartet ):
                if isinstance( equiv, BadQuartet ):
                    match.append( quartet )
                else:
                    mismatch.append( quartet )
            elif isinstance( equiv, BadQuartet ):
                mismatch.append( quartet )
            else:
                assert isinstance( quartet, Quartet )
                assert isinstance( equiv, Quartet )
                
                if quartet.get_sorted_key( key ) == equiv.get_sorted_key( key ):
                    match.append( quartet )
                else:
                    mismatch.append( quartet )
        
        return QuartetComparison( QuartetCollection( no_equiv ),
                                  QuartetCollection( lookup.values() ),
                                  QuartetCollection( match ),
                                  QuartetCollection( mismatch ),
                                  QuartetCollection( itertools.chain( self, lookup.values() ) ) )


def get_num_quartets( graph: MGraph, node_filter: UNodePredicate = None ) -> int:
    """
    Calculates the number of quartets in the `graph` given a particular `node_filter`.
    """
    nodes = realise_node_predicate_as_set( graph, node_filter )
    return array_helper.get_num_combinations(nodes, 4)


def iter_quartets( graph: MGraph, node_filter: UNodePredicate = None ) -> Iterator[Quartet]:
    """
    Iterates all quartets in the `graph`, where a quartet can contain any of the nodes defined by the `node_filter`.
    """
    nodes = realise_node_predicate_as_set( graph, node_filter )
    
    if len( nodes ) < 4:
        return
    
    for quartet in itertools.combinations( nodes, 4 ):
        yield get_quartet( graph, quartet )


def get_quartet( graph: MGraph, node_filter: UNodePredicate = None ) -> AbstractQuartet:
    """
    Given a set of nodes, what is the quartet?
    
    Uses a path-walking method from the first node to determine where the paths diverge.
    This works on DAGs also (if we allow the quartet to assume the shortest path).
    
    :param graph:           Graph 
    :param node_filter:     Nodes (must be 4!) 
    :return:                An `AbstractQuartet` object - `Quartet` or `BadQuartet`. 
    """
    quartet = frozenset( realise_node_predicate_as_set( graph, node_filter ) )
    
    if len( quartet ) != 4:
        raise ValueError( "A quartet must have 4 nodes, but {} have been provided.".format( len( quartet ) ) )
    
    a, b, c, d = quartet
    ab, ac, ad = (find_shortest_path( graph, start = a, end = n ) for n in (b, c, d))
    sp = min( len( p ) for p in (ab, ac, ad) )
    
    for i in range( 0, sp ):
        if ab[i] is ac[i]:
            if ab[i] is ad[i]:
                # B=C=D
                pass
            else:
                # B=C≠D
                return Quartet( b, c, a, d )
        elif ab[i] is ad[i]:
            # B=D≠C
            return Quartet( b, d, a, c )
        elif ac[i] is ad[i]:
            # C=D≠B
            return Quartet( c, d, a, b )
        else:
            # B≠C≠D
            return BadQuartet( a, b, c, d )
    
    return BadQuartet( a, b, c, d )


def get_quartet_directed( graph: MGraph, node_filter: UNodePredicate = None ) -> AbstractQuartet:
    """
    OBSOLETE
    Quartet method that only works on DAGs.
    """
    warnings.warn("deprecated, use `get_quartet`.", DeprecationWarning)
    quartet = frozenset( realise_node_predicate_as_set( graph, node_filter ) )
    
    if len( quartet ) != 4:
        raise ValueError( "A quartet must have 4 nodes, but {} have been provided.".format( len( quartet ) ) )
    
    mrcas = defaultdict( set )
    
    # print("**********")
    
    for pair in itertools.combinations( quartet, 2 ):
        pair = frozenset( pair )
        assert len( pair ) == 2
        try:
            mrca = find_common_ancestor( graph, pair )
        except NotFoundError:
            # print("{} ------ {}".format("NOT_FOUND", pair))
            pass
        else:
            mrcas[mrca].add( pair )
            # print("{} ------ {}".format(mrca, pair))
    
    # There will be 1 or 2 combinations that appear in a unique clade, we only need 1
    unique = None
    
    for value in mrcas.values():
        if len( value ) == 1:
            unique = array_helper.first_or_error( value )
            break
    
    if unique is None:
        return BadQuartet( *quartet )
    else:
        return Quartet( *unique, *(quartet - unique) )


def get_quartets( graph: MGraph, node_filter: UNodePredicate = None ) -> QuartetCollection:
    """
    Obtains the quartets from a graph and packages the result as a :class:`QuartetCollection`. 
    See also :func:`iter_quartets`.
    
    :param graph:           Graph. 
    :param node_filter:     Which nodes to obtain quartets on.  
    :return:                A `QuartetCollection`. 
    """
    return QuartetCollection( iter_quartets( graph, node_filter ) )


def compare_quartets( left: MGraph, right: MGraph, node_filter: UNodePredicate, key: DNodeToObject = None ) -> QuartetComparison:
    """
    Convenience method which calls `QuartetCollection.compare`.
    """
    left_quartets = get_quartets( left, node_filter )
    right_quartets = get_quartets( right, node_filter )
    
    return left_quartets.compare( right_quartets, key = key )
