import re
from os import path
from typing import Callable, Dict, FrozenSet, Iterable, List, Optional, Set, Tuple, TypeVar, Union, Sequence

from mgraph.graphing import DEdgeToText, DNodePredicate, EDirection, EGraphFormat, FollowParams, GraphRecursionError, MEdge, MGraph, MNode, MSplit, UNodeToText, DNodeToText
from mhelper import Colour, MEnum, SwitchError, array_helper, exception_helper, file_helper, string_helper, svg_helper as SVG, io_helper, TTristate


T = TypeVar( "T" )
_RX1 = re.compile( "(<[^>]+>)" )

DNodeToFormat = Callable[[MNode], "NodeStyle"]
UNodeToFormat = Union[str, DNodeToText, DNodeToFormat]
"""
Something that can be used to format a node, ONE OF:

* `None` or `""`, denoting that the string representation of the node is used as the label and default formatting is applied as per `NodeStyle.default`
* A string, denoting how to label the nodes, node attributes may be specified by placeholders as per `NodeStyle.replace_placeholders` and default formatting is applied as per `NodeStyle.default`.
* A callable, accepting an `MNode` as an argument and returning a `str`. The `str` label is handled as above.
* A callable, accepting an `MNode` and returning a `NodeStyle`, describing the node style in full.

Please note that not all formatters make use of certain node styles. For instance, newick output only uses the node labels whilst SVG output uses all parameters.
"""
DEntToProps = Callable[[Union[MNode, MEdge]], Dict[str, object]]
"""
Delegate which takes an entity (node or edge) and returns a dictionary of its properties.
"""


class EJs( MEnum ):
    VISJS = 1
    CYTOSCAPEJS = 2


class EShape( MEnum ):
    """
    Node shapes
    """
    BOX = 1
    STAR = 2
    ELLIPSE = 3
    TEXT = 4


class NodeStyle:
    def __init__( self,
                  label: str,
                  foreground: str = "#000000",
                  background: str = "#FFFFFF",
                  shape: EShape = EShape.BOX ):
        """
        Node style.
        :param label:           Label of node. 
        :param foreground:      Foreground. A string of the form "`#RRGGBB`" or "`#RRGGBBAA`".
        :param background:      Background. A string of the form "`#RRGGBB`" or "`#RRGGBBAA`".
        :param shape:           Shape of node. 
        """
        self.label = label
        self.foreground = foreground
        self.background = background
        self.shape = shape
    
    
    @classmethod
    def default( cls,
                 *,
                 node: Optional[MNode] = None,
                 label: Optional[str] = None,
                 foreground: Optional[str] = None,
                 background: Optional[str] = None,
                 shape: Optional[EShape] = None,
                 format_str: Optional[str] = None
                 ) -> "NodeStyle":
        """
        Constructs a default node style.
        
        :param node:            Node to construct style for. If not specified the "leaf node" style is assumed. 
        :param label:           Label of node. Defaults to `str(Node)`.
        :param foreground:      Foreground. Defaults dependent on `node`. 
        :param background:      Background. Defaults to colour contrasting with `foreground`.  
        :param shape:           Shape. Defaults dependent on `node`. 
        :param format_str:      Format string, overrides `label`. See :func:`replace_placeholders`.
        :return: New `NodeStyle` object. 
        """
        if format_str is not None:
            if node is None:
                raise ValueError( "`node` cannot be None when `format_str` is set." )
            
            if label is not None:
                raise ValueError( "`label` must be None when `format_str` is set." )
            
            label = cls.replace_placeholders( node, format_str )
        
        if label is None:
            if node is None:
                raise ValueError( "`node` cannot be None when `label` is not set." )
            
            label = str( node )
        
        if shape is None:
            if node is None or node.is_leaf:
                shape = EShape.BOX
            elif node.is_root:
                shape = EShape.BOX
            elif node.num_parents > 1:
                shape = EShape.STAR
            else:
                shape = EShape.ELLIPSE
        
        if background is None:
            if node is None or node.is_leaf:
                background = NodeStyle._make_unique_colour( label )
            elif node.is_root:
                background = "#800000"
            elif node.num_parents > 1:
                background = "#FF0000"
            else:
                background = "#FFFFFF"
        
        if foreground is None:
            foreground = Colour( background ).contrasting_bw().html
        
        return cls( label = label,
                    foreground = foreground,
                    background = background,
                    shape = shape )
    
    
    @staticmethod
    def replace_placeholders( node: MNode, label: str ) -> str:
        """
        Node label formatting:
        
        If the label format is blank, the node text is returned verbatim.
        
        The label format may contain any arbitrary text.
        Fields enclosed in angle bracket are replaced with that field on the node's data.
        e.g. `Accession: <accession>` uses `node.data.accession` to give `Accession: ABC123`.
        
        Fields starting `.` denote fields on the node, rather than the data.
        e.g. `Children: <.num_children>` uses `node.num_children` to give `Children: 12`.
        
        Fields ending `()` execute that method.
        e.g. `FASTA: <get_fasta()>` calls `node.data.get_fasta()` to give `FASTA: >ABC123\nCCGGTTAA`
        
        Fields may be specified at any depth.
        e.g. `Num sites: <site_array.__len__()>` calls `node.data.site_array.__len__()` to give `Num sites: 8`.
        
        :param node:        Node to format 
        :param label:       Label format 
        :return:            Formatted node label. 
        """
        if not label:
            return str( node )
        elif not isinstance( label, str ):
            raise exception_helper.type_error( "label", label, str )
        
        r = []
        
        for element in _RX1.split( label ):
            if element.startswith( "<" ):
                element = element[1:-1]
                props = element.split( "." )
                
                if not props[0]:
                    t = node
                    del props[0]
                else:
                    t = node.data
                
                for prop in props:
                    if prop.endswith( "()" ):
                        prop = prop[:-2]
                        call = True
                    else:
                        call = False
                    
                    t = getattr( t, prop )
                    
                    if call:
                        t = t()
                
                r.append( str( t ) )
            else:
                r.append( element )
        
        return "".join( r )
    
    
    @staticmethod
    def _make_unique_colour( label: str ):
        import hashlib
        hash_object = hashlib.md5( label.encode() )
        return (Colour( hash_object.hexdigest()[0:8] ) // 2).html


def export_file( graph: MGraph, file_name: str, extension: str = None, fnode: UNodeToFormat = None, fprops: DEntToProps = None ):
    if extension is None:
        extension = file_helper.get_extension( file_name )
    
    extension = extension.lower()
    
    xmap = EXTENSION_MAP.get( extension )
    
    if xmap is None:
        raise ValueError( "Cannot export file because the extension «{}» is not recognised.".format( extension ) )
    
    _, fn, flags = xmap
    
    kwargs = { }
    
    if flags & SUPPORTS_FPROPS:
        kwargs["fprops"] = fprops
    
    if flags & SUPPORTS_FNODE:
        kwargs["fnode"] = fnode
    
    fn( graph, **kwargs )


def export_binary( graph: MGraph, file_name: Optional[str] ) -> Optional[bytes]:
    """
    Saves to a pickle.
    :param graph:   Graph to export. 
    :param file_name: Filename. If `None` will return the bytes instead.
    :return:    The bytes if a filename is not provided, otherwise `None`. 
    """
    return io_helper.save_binary( file_name, graph )


def realise_node_to_format( fnode: UNodeToFormat ) -> DNodeToFormat:
    """
    Given a string format or callable, returns a callable.
    
    :param fnode: Either:
                  A callable that takes a single `MNode` argument and returns a string.
                        e.g. `lambda node: "My node is called {} and has {} children.".format( node.data.name, node.num_children )`.
                  or
                  A format string that uses `<xxx.yyy.zzz>` to denote dynamic values of the `data` property and `<.xxx.yyy.zzz>` to denote dynamic values of the node.
                        e.g. `"my node is called <name> and has <.num_children> children."`
                  Other values are undefined, if `fname` does not derive from `str` it will be assumed to be a callable.
    :return:    A callable that takes a single `MNode` argument and returns a string. 
    """
    if not fnode or isinstance( fnode, str ):
        def __implementation( node: MNode ):
            return NodeStyle.default( node = node, format_str = fnode )
        
        
        return __implementation
    else:
        def __converter( node: MNode ):
            r = fnode( node )
            
            if isinstance( r, str ):
                return NodeStyle.default( node = node, format_str = r )
            elif isinstance( r, NodeStyle ):
                return r
            else:
                raise SwitchError( "fnode(node)", r, instance = True, details = "Check your node formatter («{}») and make sure it is returning either a `str` or a `NodeStyle`.".format( fnode ) )
        
        
        return __converter


def export_cytoscape_js( *args, **kwargs ):
    """
    Exports a Cytoscape.JS HTML page.
    See `export_js` for details.
    
    :param args:        Parameters passed to export_js 
    :param kwargs:      Parameters passed to export_js
    :return:            Return value from Parameters passed to export_js 
    """
    return export_js( *args, **kwargs, js = EJs.CYTOSCAPEJS )


def export_vis_js( *args, **kwargs ):
    """
    Exports a Vis.JS HTML page.
    See `export_js` for details.
    
    :param args:        Parameters passed to export_js. 
    :param kwargs:      Parameters passed to export_js
    :return:            Return value from Parameters passed to export_js
    """
    return export_js( *args, **kwargs, js = EJs.VISJS )


def export_js( graph: MGraph,
               *,
               fnode: UNodeToFormat = None,
               inline_title: bool = False,
               title: str = None,
               rooted: TTristate = None,
               js: EJs,
               map: Optional[Dict[int, MNode]] = None ) -> str:
    """
    Creates an html/js file.
     
    :param map:                 Optional dictionary to receive the mapping of node IDs (ints) to values (MNodes) 
    :param graph:               A graph, or a sequence of one or more graphs and names.
    :param js:                  Which JS library to use.
    :param fnode:               String describing how the nodes are formatted.
                                See `specify_graph_help` for details.
    :param title:               The title of the page. When `None` a default title is suggested.
                                Note that the title will always show in the title bar, even if `inline_title` is `False`.
    :param inline_title:        When `True` an inline heading is added to the page. 
    :param rooted:              Draw a rooted graph (hierarchical).
    :return:                    A string containing the HTML. 
    """
    if js == EJs.VISJS:
        template_file = "vis_js_template.html"
        node_spec = """
        {{ 
            shape: '{SHAPE}',
            id: {ID},
            label: '{LABEL}',
            color:
            {{
                background: '{BACKGROUND}',
                highlight: '#0000FF'
            }},
            font:
            {{
                color: '{FOREGROUND}'
            }}
        }},
        """
        edge_spec = "{{ from: {SID}, to: {EID}, arrows:'to', color: {{ color: '{COLOUR}' }} }},"
    elif js == EJs.CYTOSCAPEJS:
        template_file = "cytoscape_js_template.html"
        node_spec = "{{ data: {{ id: 'n{ID}', label: '{LABEL}', color: '{BACKGROUND}' }} }},"
        edge_spec = "{{ data: {{ source: 'n{SID}', target: 'n{EID}' }} }},"
    else:
        raise SwitchError( "js", js )
    
    if title is None:
        title = ""
    
    # Parameter handling
    fnode = realise_node_to_format( fnode )
    
    # Page heading
    if inline_title:
        prefix = "<p><b>$(TITLE)</b></p><p>$(COMMENT)</p>"
    else:
        prefix = ""
    
    # Get graph information
    all_nodes = [λnode for λnode in graph.nodes]
    all_edges = [λedge for λedge in graph.edges]
    nodes = array_helper.create_index_lookup( all_nodes )
    
    if map is not None:
        for key, value in nodes.items():
            map[value] = key
    
    # Add the nodes
    node_list = []
    
    for node, node_id in nodes.items():
        assert isinstance( node, MNode )
        
        style: NodeStyle = fnode( node )
        
        node_text = node_spec.format( SHAPE = style.shape.name.lower(),
                                      ID = node_id,
                                      LABEL = style.label,
                                      BACKGROUND = style.background,
                                      FOREGROUND = style.foreground )
        
        node_list.append( node_text )
    
    # Add the edges
    edge_list = []
    
    for edge in all_edges:
        if edge.right.num_parents > 1:
            colour = "#FF0000"
        else:
            colour = "#000000"
        
        edge_text = edge_spec.format( SID = nodes[edge.left],
                                      EID = nodes[edge.right],
                                      COLOUR = colour )
        
        edge_list.append( edge_text )
    
    # Layout
    if not rooted:
        options = ''
    else:
        # noinspection SpellCheckingInspection
        options = """
        layout:
        {
            hierarchical: 
            { 
                direction: "UD", 
                sortMethod: "directed" 
            }
        },
        physics: 
        {
            hierarchicalRepulsion:
            {
                centralGravity: 0.0,
                springLength: 100,
                springConstant: 0.01,
                nodeDistance: 120,
                damping: 0.09
            },
            maxVelocity: 1,
            solver: 'hierarchicalRepulsion',
            timestep: 0.35,
            stabilization: 
            {
                enabled: true,
                iterations: 1,
                updateInterval: 25
            }
        }"""
    
    # Output the page
    HTML_T = file_helper.read_all_text( path.join( file_helper.get_directory( __file__, ), template_file ) )
    HTML_T = HTML_T.replace( "$(PREFIX)", prefix )
    HTML_T = HTML_T.replace( "$(TITLE)", title )
    HTML_T = HTML_T.replace( "$(COMMENT)", "File automatically generated by Groot. Please replace this line with your own description." )
    HTML_T = HTML_T.replace( "$(NODES)", "\n".join( node_list ) )
    HTML_T = HTML_T.replace( "$(EDGES)", "\n".join( edge_list ) )
    HTML_T = HTML_T.replace( "$(OPTIONS)", options )
    return HTML_T


def export_ancestry( graph: MGraph,
                     *,
                     fnode: UNodeToFormat = None ):
    """
    Converts the graph to a node list, with included ancestry information.
    :param graph:   Graph to export
    :param fnode:   Formatter for node names, see `to_string`.
    """
    fnode = realise_node_to_format( fnode )
    r = []
    
    for node in graph.nodes:
        if node.num_parents == 0:
            r.append( fnode( node ).label )
        elif node.num_parents == 1:
            r.append( "{} ➡ {}".format( fnode( node.parent ).label, fnode( node ).label ) )
        else:
            r.append( "({}) ➡ {}".format( string_helper.format_array( (fnode( x ) for x in node.parents), join = "+" ), fnode( node ).label ) )
    
    return "\n".join( r )


def export_compact( graph: MGraph, fnode: UNodeToFormat = None ):
    """
    Retrieves a compact string representing the graph.
    Useful for debugging.
    :param fnode: Node formatter
    :param graph: Graph to export
    """
    fnode = realise_node_to_format( fnode )
    return export_edgelist( graph, fnode = lambda x: str( fnode( x ).label ).replace( ",", "_" ).replace( "|", "¦" ), delimiter = ",", line = "|" )


def export_nodelist( graph: MGraph,
                     *,
                     fnode: UNodeToText = None ):
    """
    Lists the nodes of the graph, as text.
    :param graph:   Graph to export
    :param fnode:   Node name format
    """
    fnode = realise_node_to_format( fnode )
    r = []
    
    for node in graph:
        r.append( fnode( node ).label )
    
    return "\n".join( r )


def export_edgelist( graph: MGraph,
                     *,
                     file_name: str = "",
                     fnode: UNodeToFormat = str,
                     delimiter: str = ", ",
                     colnames: Union[bool, Sequence[str]] = True,
                     ex_colnames: Sequence[str] = None,
                     cols: int = 2,
                     ex_cols: Sequence[Callable[[MEdge], object]] = None,
                     pad: int = False,
                     line: str = "\n" ):
    """
    Converts the graph to a textual edge-list.
    
    :param graph:           Graph to export.
    :param file_name:       File to write text to (optional).
    :param fnode:           How to name the nodes (only applicable if `cols` ≠ 0).
    :param delimiter:       The delimiter to use. 
    :param colnames:        Array of the standard column names.
                            Use `False` for no column names (ignored if `ex_colnames is set).
                            Use `True` for default column names ("source", "target", "data").
                            Can also be set to array of specific names (see `std_cols`).
    :param ex_colnames:     Names of any additional columns.
    :param cols:            Standard columns
                            `0`: no standard columns
                            `2`: edge.start, edge.end
                            `3`: edge.start, edge.end, edge.data 
    :param ex_cols:         Expressions to obtain additional columns: callables that accept an edge and return a value.
    :param pad:             Pad node names to this long.
                            If this is `-1` the padding will be determined automatically.
                            If this is `0` there will be no padding.
    :param line:            Linebreak character. 
    :return:                Edgelist as a string. 
    """
    fnode = realise_node_to_format( fnode )
    
    if ex_colnames is not None:
        if not colnames:
            colnames = True
    
    if cols == 0:
        cols_ = []
        colnames_ = []
    elif cols == 2:
        cols_ = [lambda x: fnode( x.left ).label,
                 lambda x: fnode( x.right ).label]
        colnames_ = ["source", "target"]
    elif cols == 3:
        cols_ = [lambda x: fnode( x.left ).label,
                 lambda x: fnode( x.right ).label,
                 lambda x: x.data]
        colnames_ = ["source", "target", "data"]
    else:
        raise SwitchError( "cols", cols_ )
    
    if ex_cols is not None:
        cols_ = list( cols_ ) + list( ex_cols )
    
    if not colnames:
        colnames_ = None
    elif ex_colnames is not None:
        colnames_ = list( colnames_ ) + list( ex_colnames )
    
    if colnames_ is not None and len( cols_ ) != len( colnames_ ):
        raise ValueError( "Different numbers of columns and column names" )
    
    cols = len( cols_ )
    
    pads = [0] * cols
    
    if colnames_ is not None:
        for i in range( cols ):
            pads[i] = len( str( colnames_[i] ) )
    
    for edge in graph.edges:
        for i in range( cols ):
            pads[i] = max( pads[i], len( str( cols_[i]( edge ) ) ) )
    
    r = []
    
    if colnames_ is not None:
        r.append( delimiter.join( str( x ).ljust( pads[i] ) for i, x in enumerate( colnames_ ) ) )
    
    for edge in graph.edges:
        r.append( delimiter.join( str( x( edge ) ).ljust( pads[i] ) for i, x in enumerate( cols_ ) ) )
    
    res = line.join( r )
    
    if file_name:
        file_helper.write_all_text( file_name, res )
    
    return res


def export_ascii( graph: MGraph,
                  *,
                  fnode: UNodeToFormat = str,
                  direction: EDirection = EDirection.OUTGOING ):
    """
    Shows the graph as ASCII-art (UTF8).
    
    :param graph:           Graph to export
    :param direction:       Direction to follow edges. 
    :param fnode:           How to name the nodes
    """
    fnode = realise_node_to_format( fnode )
    results: List[str] = []
    
    all = set( graph )
    num_roots = 0
    
    while all:
        num_roots += 1
        results.append( "(ROOT {} OF <NUM_ROOTS>)".format( num_roots ) )
        root = __suggest_root( graph, all, direction )
        params = graph.follow( FollowParams( start = root, include_repeats = True, direction = direction ) )
        __remove_touched( all, params.visited_nodes )
        results.extend( x.describe( fnode ) for x in params.visited )
    
    if num_roots == 1:
        del results[0]
    
    return "\n".join( results ).replace( "<NUM_ROOTS>", str( num_roots ) )


def export_newick( graph: MGraph,
                   *,
                   fnode: UNodeToFormat = str,
                   direction: EDirection = EDirection.OUTGOING,
                   fedge: Optional[DEdgeToText] = None,
                   internal: bool = True,
                   multi_root: bool = False ):
    """
    Converts the graph to a Newick tree (or trees if there are multiple roots).
    
    :param graph:        Graph to export
    :param direction:    Direction to follow edges 
    :param fnode:        How to name the nodes
    :param fedge:        How to name the edges  
    :param internal:     Whether to name internal nodes
    :param multi_root:    Permit export of trees with multiple roots (one tree per line).
    :return:             Newick tree, as a string. 
    """
    all = set( graph )
    r = []
    
    while all:
        root = __suggest_root( graph, all, direction )
        touched = set()
        try:
            r.append( __node_to_newick( root, fnode, fedge, direction, internal, None, touched ) + ";" )
        except GraphRecursionError as ex:
            raise GraphRecursionError( "Cannot convert the graph to Newick because it has loops.", ex.nodes ) from ex
        
        assert touched
        __remove_touched( all, touched )
        
        if not multi_root and all:
            raise ValueError( "Cannot export this graph to Newick format because it has multiple roots: ".format( string_helper.format_array( graph.nodes.roots ) ) )
    
    return "\n".join( r )


def export_ete( graph: MGraph,
                *,
                fnode: UNodeToFormat = None ):
    """
    Converts the graph to an Ete tree.
    Requires library: `ete`.
    
    :remarks:
    At the time of writing, the Ete code doesn't appear to handle multi-rooted trees
    and therefore Ete's behaviour with non-treelike graphs is undefined. 
    
    :param graph:   Graph to export
    :param fnode:   How to format nodes.
    :return: An arbitrary node from the resulting Ete tree.
    """
    from ete3 import TreeNode
    fnode = realise_node_to_format( fnode )
    
    map = { }
    
    
    def __recurse( m_node: MNode ) -> TreeNode:
        if m_node in map:
            return map[m_node]
        
        e_node = TreeNode( name = fnode( m_node ).label )
        map[m_node] = e_node
        
        for m_child in m_node.edges.list_nodes( EDirection.OUTGOING ):
            e_child = __recurse( m_child )
            # noinspection PyTypeChecker
            e_node.add_child( e_child )
        
        return e_node
    
    
    r = None
    
    for node in graph:
        r = __recurse( node )
    
    return r


def export_string( graph: MGraph,
                   format: EGraphFormat,
                   fnode: UNodeToFormat = str ):
    """
    Converts the graph to text.
    Default options are used. Use :function:export_newick, :function:export_ascii, etc. to provide more options.  
    
    :param graph:       Graph to export
    :param format:      Format 
    :param fnode:       How to name the nodes 
    :return:            Text
    """
    if format == EGraphFormat.NEWICK:
        return export_newick( graph = graph, fnode = fnode )
    elif format == EGraphFormat.NODELIST:
        return export_nodelist( graph = graph, fnode = fnode )
    elif format == EGraphFormat.ANCESTRY:
        return export_ancestry( graph = graph, fnode = fnode )
    elif format == EGraphFormat.ASCII:
        return export_ascii( graph = graph, fnode = fnode )
    elif format == EGraphFormat.CSV:
        return export_edgelist( graph = graph, fnode = fnode )
    elif format == EGraphFormat.TSV:
        return export_edgelist( graph = graph, fnode = fnode, delimiter = "\t" )
    elif format == EGraphFormat.COMPACT:
        return export_compact( graph = graph )
    elif format == EGraphFormat.ETE_ASCII:
        return export_ete( graph = graph, fnode = fnode ).get_ascii()
    else:
        raise SwitchError( "format", format )


def __suggest_root( graph: MGraph, subset: Set["MNode"], direction: EDirection ) -> "MNode":
    for node in graph.iter_roots( subset, direction ):
        return node


def __remove_touched( all, touched ):
    for node in touched:
        if node in all:
            all.remove( node )


def __node_to_newick( node: MNode,
                      fnode: UNodeToFormat,
                      fedge: Optional[DEdgeToText] = None,
                      direction: EDirection = EDirection.OUTGOING,
                      internal: bool = True,
                      origin: Optional[MEdge] = None,
                      touched: Set["MNode"] = None ):
    """
    Resolves this node to Newick.
    This is used by the :func:`mgraph.exporting.export_newick`.
    
    :param node:            Node
    :param internal:        Whether to name internal nodes
    :param fedge:           How to obtain edge names
    :param fnode:           How to obtain node names 
    :param origin:          When set, will not follow to this relation 
    :param direction:       Direction to follow edges
    :param touched:         Set of touched nodes. 
    :return:                Newick string 
    """
    
    # Parameters
    if touched is None:
        touched = set()
    
    fnode = realise_node_to_format( fnode )
    
    # Loop detection
    if node in touched:
        raise GraphRecursionError( "`__node_to_newick` recurring to same node..", [node] )
    
    touched.add( node )
    
    # Get outgoing edges
    edges = node.edges.by_direction( direction )
    
    if origin in edges:
        edges.remove( origin )
    
    # Name the incoming edge
    if origin is not None and fedge is not None:
        edge_txt = fedge( origin )
        if edge_txt:
            edge_txt = ":" + edge_txt
    else:
        edge_txt = ""
    
    # Lone node, simple format
    if not edges:
        return fnode( node ).label + edge_txt
    
    # Concatenate the children
    try:
        children_str = ",".join( __node_to_newick( edge.opposite( node ), fnode = fnode, fedge = fedge, direction = direction, internal = internal, origin = edge, touched = touched ) for edge in edges )
    except GraphRecursionError as ex:
        raise GraphRecursionError( "`__node_to_newick` recurring.", [node] + ex.nodes )
    
    # Format the results
    return "(" + children_str + ")" + (fnode( node ).label if internal else "") + edge_txt


def __export_splits_iter( graph: MGraph, filter: DNodePredicate = None, gdata: Callable[[MNode], T] = None ) -> Iterable[Tuple[FrozenSet[T], FrozenSet[T]]]:
    """
    Iterates the set of splits in a graph.
    See :func:`export_splits` for parameter details.
    
    :return:    Iterable of splits (tuple):
                    1. Left set of split (`node.data` where `leaf_definition(node)` is `True`)
                    2. Right set of split 
    """
    if filter is None:
        filter = lambda x: x.is_leaf
    
    if gdata is None:
        gdata = lambda x: x.data
    
    all_sequences = set( gdata( x ) for x in graph if filter( x ) )
    
    for edge in graph.edges:
        left_all = graph.follow( FollowParams( start = edge.left, edge_filter = lambda x: x is not edge ) ).visited_nodes
        left_leaves = set( gdata( x ) for x in left_all if filter( x ) )
        right_leaves = all_sequences - left_leaves
        yield frozenset( left_leaves ), frozenset( right_leaves )


def export_splits( graph: MGraph, *, filter: DNodePredicate = None, gdata: Callable[[MNode], object] = None ) -> Set[MSplit]:
    """
    Obtains the set of splits in a graph.
    See :class:`Split`.
    
    :param graph:       Graph 
    :param filter:      Definition of a leaf node. `node.is_leaf` by default.
                        ( we _can_ create splits of internal nodes too, we just can't _recreate_ such splits )
    :param gdata:       How to retrieve data from node. `node.data` by default.
                        Note that data must be _unique_, if two nodes share the same `gdata` result then they will be considered equivalent. 
    :return:            Set of splits as :class:`Split` objects. 
    """
    all_splits: Set[MSplit] = set()
    
    for left_sequences, right_sequences in __export_splits_iter( graph, filter, gdata ):
        all_splits.add( MSplit( left_sequences, right_sequences ) )
        all_splits.add( MSplit( right_sequences, left_sequences ) )
    
    return all_splits


def export_svg( graph: MGraph, html: bool = False, fnode: UNodeToFormat = None, title: str = None ) -> str:
    """
    Exports a tree-like SVG.
    
    :param graph:   Graph 
    :param html:    When `True` include an HTML header instead of an SVG one.
    :param fnode:   Node text 
    :param title:   SVG or HTML title. 
    :return:        SVG/HTML text as string. 
    """
    fnode = realise_node_to_format( fnode )
    
    # Constants
    from mgraph import analysing
    _x_ = 64
    _y_ = 32
    _sx_ = _x_
    _sy_ = _y_ + 48
    _size_ = SVG.Point( _x_, _y_ )
    
    # X positions of the nodes first
    P: Dict[MNode, SVG.Point] = { }
    leaf_index = 0
    leaves = set()
    roots = set( graph.nodes.roots )
    
    for ns in analysing.iter_depth_first( graph, roots, sort = lambda x: len( x.list_descendants() ) ):
        n = ns.node
        assert n not in leaves
        leaves.add( n )
        P[n] = SVG.Point( leaf_index * _sx_, 0 )
        if n.is_leaf or len( roots ) > 1:
            leaf_index += 1
    
    # Parents get X-averaged across their children
    for ns in analysing.iter_breadth_first( graph, leaves ):
        n = ns.node
        
        if n.is_leaf:
            continue
        
        x = 0
        
        for c in n.children:
            x += P[c].x
        
        x /= n.num_children
        
        P[n] = SVG.Point( x, 0 )
    
    # Everything gets Y-positioned by its breadth-first distance from the root
    for n in analysing.iter_breadth_first( graph, roots ):
        P[n.node].y = n.distance * _sy_
    
    # Draw things
    w = SVG.SvgWriter( enable_html = html,
                       title = title )
    
    for node in graph:
        style = fnode( node )
        rc = P[node]
        
        if style.shape == EShape.BOX:
            rcc = w.add_rect( loc = rc, size = _size_, fill = style.background, stroke = style.foreground )
        elif style.shape == EShape.ELLIPSE:
            rcc = w.add_ellipse( loc = rc, size = _size_, fill = style.background, stroke = style.foreground )
        else:
            rcc = w.add_rect( loc = rc, size = _size_, fill = style.background, stroke = style.background )
        
        w.add_text( loc = rcc.centre,
                    text = fnode( node ).label,
                    alignment_baseline = SVG.EAlignmentBaseline.middle,
                    text_anchor = SVG.ETextAnchor.middle )
    
    for node in graph:
        rc = P[node]
        for child in node.children:
            crc = P[child]
            w.add_line( loc1 = SVG.Point( rc.x + _size_.x / 2, rc.y + _size_.y ), loc2 = SVG.Point( crc.x + _size_.x / 2, crc.y ), stroke = "black" )
    
    return w.to_string()


def export_gexf( graph: MGraph, fprops: DEntToProps = None ) -> str:
    TEMPLATE = \
        """
        <gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
            <graph mode="static" defaultedgetype="directed">
                <attributes class="node">
    {0}
                </attributes>
                <attributes class="edge">
    {1}
                </attributes>
                <nodes>
    {2}
                </nodes>
                <edges>
    {3}
                </edges>
            </graph>
        </gexf>
        """
    
    if fprops is None:
        fprops = lambda x: { }
    
    nodes = array_helper.create_index_lookup( graph.nodes )
    edges = array_helper.create_index_lookup( graph.edges )
    
    node_xml = []
    edge_xml = []
    node_attrs = { }
    node_attr_xml = []
    edge_attrs = { }
    edge_attr_xml = []
    
    for node, node_id in nodes.items():
        node_xml.append( '                <node id="{0}" label="{1}">'.format( node_id, node.label ) )
        __write_attributes( node, node_attr_xml, node_attrs, node_xml, fprops )
        node_xml.append( '                </node>' )
    
    for edge, edge_id in edges.items():
        start_id = nodes[edge.start]
        end_id = nodes[edge.end]
        edge_xml.append( '                <edge id="{0}" label="{1}" source="{2}" target="{3}">'.format( edge_id, edge.label, start_id, end_id ) )
        __write_attributes( edge, edge_attr_xml, edge_attrs, edge_xml, fprops )
        edge_xml.append( '                </edge>' )
    
    return TEMPLATE.format( "\n".join( node_attr_xml ), "\n".join( edge_attr_xml ), "\n".join( node_xml ), "\n".join( edge_xml ) )


def __write_attributes( entity: Union[MEdge, MNode], attr_xml: List[str], attrs, xml: List[str], fprops: DEntToProps ):
    xml.append( '                    <attvalues>' )
    
    props = fprops( entity )
    
    for k, v in props.items():
        if k not in attrs:
            aid = len( attrs )
            attrs[k] = aid
            attr_xml.append( '                <attribute id="{0}" title="{1}" type="string"/>'.format( aid, k ) )
        else:
            aid = attrs[k]
        
        vstr = str( v )
        vstr = vstr.replace( "<", "&apos;&lt;&apos;" ).replace( ">", "&apos;&gt;&apos;" )  # causes Gephi error
        xml.append( '                        <attvalue for="{0}" value="{1}"/>'.format( aid, vstr ) )
    xml.append( '                    </attvalues>' )


SUPPORTS_FPROPS = 1
SUPPORTS_FNODE = 2

EXTENSION_MAP = { ".html": ("Vis.js - Webpage", export_vis_js, SUPPORTS_FNODE),
                  ".htm" : ("Cytoscape.js - Webpage", export_cytoscape_js, SUPPORTS_FNODE),
                  ".csv" : ("CSV - Excel", export_edgelist, SUPPORTS_FNODE),
                  ".pkl" : ("Pickle - Python", export_binary, 0),
                  ".nfo" : ("ASCII art - Text", export_ascii, SUPPORTS_FNODE),
                  ".gexf": ("XML - Gephi/Cytoscape", export_gexf, SUPPORTS_FPROPS), }
"""
Mapping of file extensions to export methods.
key: extension in lower case
value: tuple:
        field 0: the description of the extension (guarenteed)
        field 1: export method (subject to change)
        field 2: export flags (subject to change) 
"""
