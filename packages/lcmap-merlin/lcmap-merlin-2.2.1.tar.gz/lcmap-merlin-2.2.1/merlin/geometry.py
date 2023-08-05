from cytoolz import get_in
import functools
import logging
import numpy as np


logger = logging.getLogger(__name__)


def minbox(points):
    """Returns the minimal bounding box necessary to contain points

    Args:
        points (tuple, list, set): ((0,0), (40, 55), (66, 22))

    Returns:
        dict: {ulx, uly, lrx, lry}

    Example:
        >>> minbox((0, 0), (40, 55), (66,22))
        {'ulx': 0, 'uly': 55, 'lrx': 66, 'lry': 0}
    """

    x, y = [point[0] for point in points], [point[1] for point in points]
    return {'ulx': min(x), 'lrx': max(x), 'lry': min(y), 'uly': max(y)}


@functools.singledispatch
def coordinates(points, grid, snap_fn):
    """Returns grid coordinates contained within points.

    Points may be specified as dicts, tuples, lists, or sets.
     
        - dict with keys ulx, uly, lrx, lry
        - sequence of sequences: ((0,0), (100, 167), (-212, 6621))

    Irregular perimeters may be specified in sequences as points will be minboxed.
    
    Points as dicts are an implicit minbox.

    Args:
        points (collection): Points outlining an area
        grid (dict)        : The target grid: {'name': 'chip', 'sx': 3000, 'sy': 3000, 'rx': 1, 'ry': -1}
        snap_fn (func)     : A function that accepts x, y and returns a snapped x, y

    Returns:
        tuple: tuple of tuples of grid coordinates ((x1,y1), (x2,y2) ...)

    Example:
        >>> grid = {'name': 'chip', 'sx': 500, 'sy': 500, 'rx': 1, 'ry': 1}
        >>> sfn = partial(chipmunk.snap, url='http://localhost:5656')
        >>> coordinates({'ulx': -1001, 'uly': 1000, 'lrx': -500, 'lry': 500}, 
                        grid=grid, 
                        snap_fn=sfn)
        ((-3585.0, 2805.0),
         (-3085.0, 2805.0),
         (-2585.0, 2805.0),
         (-2085.0, 2805.0),
         (-1585.0, 2805.0),
         (-1085.0, 2805.0),
         (-585.0, 2805.0))
        
        >>> grid = {'name': 'chip', 'sx': 3000, 'sy': 3000, 'rx': 1, 'ry': -1}
        >>> coordinates(((112, 443), (112, 500), (100, 443)),
                        grid=grid, 
                        snap_fn=sfn})
        ((-585.0, 2805.0),)
    """
    
    logger.warn("coordinates() not implemented for type:{}".format(type(points)))
    return None


@coordinates.register(dict)
def _(points, grid, snap_fn):
    """Returns grid coordinates contained within a dict of points.

    Args:
        points  (dict): {'ulx': 0, 'uly': 15.5, 'lrx': 55.3, 'lry':-1000.12}
        grid    (dict): The target grid: {'name': 'chip', 'sx': 3000, 'sy': 3000, 'rx': 1, 'ry': -1}
        snap_fn (func): A function that accepts x, y and returns a snapped x, y

    Returns:
        tuple: tuple of tuples of grid coordinates ((x1,y1), (x2,y1) ...)

    This example assumes a grid size of 500x500 pixels.

    Example:
        >>> coordinates = coordinates({ulx: -1001, uly: 1000, lrx: -500, lry: 500},
                                      grid={'name': 'chip', 'sx': 500, 'sy': 500, 'rx': 1, 'ry': -1}, 
                                      snap_fn=some_func)

        ((-1000, 500), (-500, 500), (-1000, -500), (-500, -500))
    """
    
    # snap start/end x & y
    start_x, start_y = get_in([grid.get('name'), 'proj-pt'], snap_fn(x=points.get('ulx'), y=points.get('uly')))
    end_x,   end_y   = get_in([grid.get('name'), 'proj-pt'], snap_fn(x=points.get('lrx'), y=points.get('lry')))

    # get x and y scale factors multiplied by reflection
    x_interval = grid.get('sx') * grid.get('rx')
    y_interval = grid.get('sy') * grid.get('ry')
    
    return tuple((x, y) for x in np.arange(start_x, end_x + x_interval, x_interval)
                        for y in np.arange(start_y, end_y + y_interval, y_interval))


@coordinates.register(tuple)
@coordinates.register(list)
@coordinates.register(set)
def _(points, grid, snap_fn):
    """Returns coordinates from a sequence of points.  Performs minbox
    operation on points, thus irregular geometries may be supplied.

    Args:
        points        : a sequence (list, tuple or set) of coordinates.
        grid (dict)   : {'name': 'chip', 'sx': 3000, 'sy': 3000, 'rx': 1, 'ry': -1}
        snap_fn (func): A function that accepts x, y and returns snapped x,y

    Returns:
        tuple: chip coordinates

    Example:
        >>> xys = coordinates(((112, 443), (112, 500), (100, 443)),
                              grid={'sx': 3000, 'sy': 3000}, 
                              snap_fn=some_func})
        >>> ((100, 500),)
    """

    return coordinates(minbox(points), grid=grid, snap_fn=snap_fn)


def extents(ulx, uly, grid):
    """Given an ulx, uly and grid, returns the grid extents.  

    ulx and uly are not translated during this calculation.
 
    Args:
        ulx (float): 0
        uly (float): 0
        grid (dict): {'rx', 'ry', 'sx', 'sy'}

    Returns:
        dict: {'ulx', 'uly', 'lrx', 'lry'}

    Example:
        >>> extents(ulx=0, 
                    uly=0, 
                    grid={'rx': 1, 'ry': -1, 'sx': 3000, 'sy': 3000}
        {'ulx': 0, 'uly': 0, 'lrx': 2999, 'lry': -2999}
    """
    
    return {'ulx': ulx,
            'uly': uly,
            'lrx': ulx + (grid.get('rx') * grid.get('sx')) - int(np.sign(grid.get('rx'))),
            'lry': uly + (grid.get('ry') * grid.get('sy')) - int(np.sign(grid.get('ry')))}
