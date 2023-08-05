from cytoolz import first
from cytoolz import filter
from merlin import cfg
from merlin import geometry as g
import test


def chip_grid(config):
    return first(filter(lambda x: x['name'] == 'chip', config.get('grid_fn')()))


def tile_grid(config):
    return first(filter(lambda x: x['name'] == 'tile', config.get('grid_fn')()))


def test_minbox():
    one = {'ulx': 0, 'uly': 0, 'lrx': 0, 'lry': 0}
    assert g.minbox(((0,0),)) == one

    two = {'ulx': 0, 'uly': 10, 'lrx': 10, 'lry': 0}
    assert g.minbox(((0,0), (10, 10))) == two

    three = {'ulx': -50, 'uly': 3, 'lrx': 10, 'lry': -8}
    assert g.minbox(((-50,0), (10, 3), (5, -8))) == three

    four = {'ulx': -5, 'uly': 33, 'lrx': 111, 'lry': -66}
    assert g.minbox(((0, 11), (-5, -5), (3, 33), (111, -66))) == four

    five = {'ulx': -5 , 'uly': 5 , 'lrx': 4 , 'lry': -4 }
    assert g.minbox(((1, 1), (2, 2), (-3, -3), (4, -4), (-5, 5))) == five


@test.vcr.use_cassette(test.cassette)
def test_coordinates():
    _cfg = cfg.get('chipmunk-ard', env=test.env)
    grid = chip_grid(_cfg)
    sfn  = _cfg.get('snap_fn')
    
    expected = ((-585.0, 2805.0), (-585.0, -195.0), (2415.0, 2805.0), (2415.0, -195.0))
    result   = g.coordinates({'ulx': 0, 'uly': 0, 'lrx': 3000, 'lry': -3000}, grid=grid, snap_fn=sfn)
    assert expected == result

    grid     = tile_grid(_cfg)
    expected = ((-15585.0, 14805.0),)
    result = g.coordinates({'ulx': 0, 'uly': 0, 'lrx': 3000, 'lry': -3000}, grid=grid, snap_fn=sfn)
    assert expected == result

    grid     = chip_grid(_cfg)
    expected = ((-3585.0, 5805.0), (-3585.0, 2805.0), (-585.0, 5805.0), (-585.0, 2805.0))
    result   = g.coordinates(((0, 0), (-590, 0), (0, 2806)), grid=grid, snap_fn=sfn)
    assert expected == result

    grid     = chip_grid(_cfg)
    expected = ((-3585.0, 5805.0), (-3585.0, 2805.0), (-585.0, 5805.0), (-585.0, 2805.0))
    result   = g.coordinates([(0, 0), (-590, 0), (0, 2806)], grid=grid, snap_fn=sfn)
    assert expected == result

    grid     = chip_grid(_cfg)
    expected = ((-3585.0, 5805.0), (-3585.0, 2805.0), (-585.0, 5805.0), (-585.0, 2805.0))
    result   = g.coordinates(set(((0, 0), (-590, 0), (0, 2806))), grid=grid, snap_fn=sfn)
    assert expected == result


def tests_extents():
    results = g.extents(ulx=0, uly=0, grid={'rx': 1, 'ry': -1, 'sx': 3000, 'sy': 3000})
    assert results == {'ulx': 0, 'uly': 0, 'lrx': 2999, 'lry': -2999}
