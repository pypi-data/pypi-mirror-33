#!/usr/bin/env python
"""The ``add_staff_relationships.py`` script automates adding
the relationships of some staff-related symbols to staffs.
The symbols in question are:

* ``staff_grouping``
* ``measure_separator``
* ``repeat``
* ``key_signature``
* ``time_signature``
* ``g-clef``, ``c-clef``, ``f-clef``

"""
from __future__ import print_function, unicode_literals, division
import argparse
import collections
import logging
import os
import pprint
import time

from muscima.inference_engine_constants import InferenceEngineConstants as _CONST
from muscima.io import parse_cropobject_list, export_cropobject_list
from muscima.cropobject import link_cropobjects

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


##############################################################################

ON_STAFFLINE_RATIO_TRHESHOLD = 0.15

STAFFLINE_CLSNAME = 'staff_line'
STAFFSPACE_CLSNAME = 'staff_space'
STAFF_CLSNAME = 'staff'

STAFF_RELATED_CLSNAMES = {
    'staff_grouping',
    'measure_separator',
    'key_signature',
    'time_signature',
    'g-clef', 'c-clef', 'f-clef', 'other-clef',
}

NOTEHEAD_CLSNAMES = {
    'notehead-full',
    'notehead-empty',
    'grace-notehead-full',
    'grace-notehead-empty',
}

REST_CLSNAMES = {
    'whole_rest',
    'half_rest',
    'quarter_rest',
    '8th_rest',
    '16th_rest',
    '32th_rest',
    '64th_and_higher_rest',
    'multi-measure_rest',
}


# Notes will get added separately.

##############################################################################

def add_staff_relationships(cropobjects,
                            notehead_staffspace_threshold=0.2):
    _cropobjects_dict = {c.objid: c for c in cropobjects}

    ON_STAFFLINE_RATIO_TRHESHOLD = notehead_staffspace_threshold

    ##########################################################################
    logging.info('Find the staff-related symbols')
    staffs = [c for c in cropobjects if c.clsname == _CONST.STAFF_CLSNAME]

    staff_related_symbols = collections.defaultdict(list)
    notehead_symbols = collections.defaultdict(list)
    rest_symbols = collections.defaultdict(list)
    for c in cropobjects:
        if c.clsname in _CONST.STAFF_RELATED_CLSNAMES:
            staff_related_symbols[c.clsname].append(c)
        if c.clsname in _CONST.NOTEHEAD_CLSNAMES:
            notehead_symbols[c.clsname].append(c)
        if c.clsname in _CONST.REST_CLSNAMES:
            rest_symbols[c.clsname].append(c)

    ##########################################################################
    logging.info('Adding staff relationships')
    #  - Which direction do the relationships lead in?
    #    Need to define this.
    #
    # Staff -> symbol?
    # Symbol -> staff?
    # It does not really matter, but it's more intuitive to attach symbols
    # onto a pre-existing staff. So, symbol -> staff.
    for clsname, cs in staff_related_symbols.items():
        for c in cs:
            # Find the related staff. Relatedness is measured by row overlap.
            # That means we have to modify the staff bounding box to lead
            # from the leftmost to the rightmost column. This holds
            # especially for the staff_grouping symbols.
            for s in staffs:
                st, sl, sb, sr = s.bounding_box
                sl = 0
                sr = max(sr, c.right)
                if c.overlaps((st, sl, sb, sr)):
                    link_cropobjects(c, s)

    ##########################################################################
    logging.info('Adding rest --> staff relationships.')
    for clsname, cs in rest_symbols.items():
        for c in cs:
            closest_staff = min([s for s in staffs],
                                key=lambda x: ((x.bottom + x.top) / 2. - (c.bottom + c.top) / 2.) ** 2)
            link_cropobjects(c, closest_staff)

    ##########################################################################
    logging.info('Adding notehead relationships.')

    # NOTE:
    # This part should NOT rely on staffspace masks in any way!
    # They are highly unreliable.

    # Sort the staff objects top-down. Assumes stafflines do not cross,
    # and that there are no crazy curves at the end that would make the lower
    # stafflines stick out over the ones above them...
    stafflines = [c for c in cropobjects if c.clsname == _CONST.STAFFLINE_CLSNAME]
    stafflines = sorted(stafflines, key=lambda c: c.top)
    staffspaces = [c for c in cropobjects if c.clsname == _CONST.STAFFSPACE_CLSNAME]
    staffspaces= sorted(staffspaces, key=lambda c: c.top)
    staves = [c for c in cropobjects if c.clsname == _CONST.STAFF_CLSNAME]
    staves = sorted(staves, key=lambda c: c.top)

    # Indexing data structures.
    #
    # We need to know:
    #  - per staffline and staffspace: its containing staff
    _staff_per_ss_sl = {}
    #  - per staffline and staffspace: its index (top to bottom) within the staff
    _ss_sl_idx_wrt_staff = {}
    # Reverse indexes:
    # If I know which staff (by objid) and which index of staffline/staffspace,
    # I want to retrieve the given staffline/staffspace CropObject:
    _staff_and_idx2ss = collections.defaultdict(dict)
    _staff_and_idx2sl = collections.defaultdict(dict)

    # Build the indexes
    for _staff in staves:
        # Keep the top-down ordering from above:
        _s_stafflines = [_staffline for _staffline in stafflines
                         if _staff.objid in _staffline.inlinks]
        _s_staffspaces = [_staffspace for _staffspace in staffspaces
                          if _staff.objid in _staffspace.inlinks]
        for i, _sl in enumerate(_s_stafflines):
            _staff_per_ss_sl[_sl.objid] = _staff
            _ss_sl_idx_wrt_staff[_sl.objid] = i
            _staff_and_idx2sl[_staff.objid][i] = _sl
            logging.debug('Staff {0}: stafflines {1}'.format(_staff.objid,
                                                             _staff_and_idx2sl[_staff.objid]))
        for i, _ss in enumerate(_s_staffspaces):
            _staff_per_ss_sl[_ss.objid] = _staff
            _ss_sl_idx_wrt_staff[_ss.objid] = i
            _staff_and_idx2ss[_staff.objid][i] = _ss

    # pprint.pprint(_ss_sl_idx_wrt_staff)
    logging.debug(pprint.pformat(dict(_staff_and_idx2ss)))
    # pprint.pprint(dict(_staff_and_idx2sl))

    # # Get bounding box of all participating symbols
    # notehead_staff_bbox_coords = [c.bounding_box
    #                               for c in list(itertools.chain(*notehead_symbols.values()))
    #                                        + stafflines
    #                                        + staffspaces
    #                                        + staves]
    # t, l, b, r = min([b[0] for b in notehead_staff_bbox_coords]), \
    #              min([b[1] for b in notehead_staff_bbox_coords]), \
    #              max([b[2] for b in notehead_staff_bbox_coords]), \
    #              max([b[3] for b in notehead_staff_bbox_coords])
    #
    # h, w = b - t, r - l
    # # Maybe later: ensure a 1-px empty border? (h+2, w+2) and the appropriate +1 when
    # # projecting cropobjects onto the canvas...
    # staffline_canvas = numpy.zeros((h, w), dtype='uint8')
    # for s in stafflines:
    #     dt, dl, db, dr = s.top - t, s.left - l, s.bottom - t, s.right - l
    #     staffline_canvas[dt:db, dl:dr] += s.mask

    for clsname, cs in notehead_symbols.items():
        for c in cs:

            ct, cl, cb, cr = c.bounding_box

            ################
            # Add relationship to given staffline or staffspace.

            # If notehead has ledger lines, skip it for now.
            _has_ledger_line = False
            for o in c.outlinks:
                if _cropobjects_dict[o].clsname == 'ledger_line':
                    _has_ledger_line = True
                    break

            if _has_ledger_line:
                # Attach to the appropriate staff:
                # meaning, staff closest to the innermost ledger line.
                lls = [_cropobjects_dict[o] for o in c.outlinks
                       if _cropobjects_dict[o].clsname == 'ledger_line']
                # Furthest from notehead's top is innermost.
                # (If notehead is below staff and crosses a ll., one
                #  of these numbers will be negative. But that doesn't matter.)
                ll_max_dist = max(lls, key=lambda ll: ll.top - c.top)
                # Find closest staff to max-dist ledger ine
                staff_min_dist = min(staves,
                                     key=lambda ss: min((ll_max_dist.bottom - ss.top) ** 2,
                                                        (ll_max_dist.top - ss.bottom) ** 2))
                link_cropobjects(c, staff_min_dist)
                continue

            # - Find the related staffline.
            # - Because of curved stafflines, this has to be done w.r.t.
            #   the horizontal position of the notehead.
            # - Also, because stafflines are NOT filled in (they do not have
            #   intersections annotated), it is necessary to use a wider
            #   window than just the notehead.
            # - We will assume that STAFFLINES DO NOT CROSS.
            #   (That is a reasonable assumption.)
            #
            # - For now, we only work with more or less straight stafflines.

            overlapped_stafflines = []
            overlapped_staffline_idxs = []
            for i, s in enumerate(stafflines):
                # This is the assumption of straight stafflines!
                if (ct <= s.top <= cb) or (ct <= s.bottom <= cb):
                    overlapped_stafflines.append(s)
                    overlapped_staffline_idxs.append(i)

            if c.objid < 10:
                logging.debug('Notehead {0} ({1}): overlaps {2} stafflines'.format(c.uid,
                                                                                   c.bounding_box,
                                                                                   len(overlapped_stafflines),
                                                                                   ))

            if len(overlapped_stafflines) == 1:
                s = overlapped_stafflines[0]
                dtop = s.top - ct
                dbottom = cb - s.bottom
                if min(dtop, dbottom) / max(dtop, dbottom) < ON_STAFFLINE_RATIO_TRHESHOLD:
                    logging.info('Notehead {0}, staffline {1}: very small ratio {2:.2f}'
                                  ''.format(c.objid, s.objid, min(dtop, dbottom) / max(dtop, dbottom)))
                    # Staffspace?
                    #
                    # To get staffspace:
                    #  - Get orientation (below? above?)
                    _is_staffspace_above = False
                    if dtop > dbottom:
                        _is_staffspace_above = True

                    #  - Find staffspaces adjacent to the overlapped staffline.
                    # NOTE: this will fail with single-staffline staves, because
                    #       they do NOT have the surrounding staffspaces defined...
                    _staffline_idx_wrt_staff = _ss_sl_idx_wrt_staff[s.objid]
                    if _is_staffspace_above:
                        _staffspace_idx_wrt_staff = _staffline_idx_wrt_staff
                    else:
                        _staffspace_idx_wrt_staff = _staffline_idx_wrt_staff + 1

                    # Retrieve the given staffsapce
                    _staff = _staff_per_ss_sl[s.objid]
                    tgt_staffspace = _staff_and_idx2ss[_staff.objid][_staffspace_idx_wrt_staff]
                    # Link to staffspace
                    link_cropobjects(c, tgt_staffspace)
                    # And link to staff
                    _c_staff = _staff_per_ss_sl[tgt_staffspace.objid]
                    link_cropobjects(c, _c_staff)

                else:
                    # Staffline!
                    link_cropobjects(c, s)
                    # And staff:
                    _c_staff = _staff_per_ss_sl[s.objid]
                    link_cropobjects(c, _c_staff)

            elif len(overlapped_stafflines) == 0:
                # Staffspace!
                # Link to the staffspace with which the notehead has
                # greatest vertical overlap.
                #
                # Interesting corner case:
                # Sometimes noteheads "hang out" of the upper/lower
                # staffspace, so they are not entirely covered.
                overlapped_staffspaces = {}
                for _ss_i, s in enumerate(staffspaces):
                    if s.top <= c.top <= s.bottom:
                        overlapped_staffspaces[_ss_i] = min(s.bottom, c.bottom) - c.top
                    elif c.top <= s.top <= c.bottom:
                        overlapped_staffspaces[_ss_i] = s.bottom - max(c.top, s.top)

                if len(overlapped_staffspaces) == 0:
                    logging.warn('Notehead {0}: no overlapped staffline object, no ledger line!'
                                 ''.format(c.uid))
                _ss_i_max = max(overlapped_staffspaces.keys(),
                                key=lambda x: overlapped_staffspaces[x])
                max_overlap_staffspace = staffspaces[_ss_i_max]
                link_cropobjects(c, max_overlap_staffspace)
                _c_staff = _staff_per_ss_sl[max_overlap_staffspace.objid]
                link_cropobjects(c, _c_staff)

            elif len(overlapped_stafflines) == 2:
                # Staffspace between those two lines.
                s1 = overlapped_stafflines[0]
                s2 = overlapped_stafflines[1]

                _staff1 = _staff_per_ss_sl[s1.objid]
                _staff2 = _staff_per_ss_sl[s2.objid]
                if _staff1.objid != _staff2.objid:
                    raise ValueError('Really weird notehead overlapping two stafflines'
                                     ' from two different staves: {0}'.format(c.uid))

                _staffspace_idx = _ss_sl_idx_wrt_staff[s2.objid]
                s = _staff_and_idx2ss[_staff2.objid][_staffspace_idx]
                link_cropobjects(c, s)
                # And link to staff:
                _c_staff = _staff_per_ss_sl[s.objid]
                link_cropobjects(c, _c_staff)

            elif len(overlapped_stafflines) > 2:
                raise ValueError('Really weird notehead overlapping more than 2 stafflines:'
                                 ' {0}'.format(c.uid))

    ##########################################################################
    logging.info('Attaching clefs to stafflines [NOT IMPLEMENTED].')
    clefs = [c for c in cropobjects if c.clsname in ['g-clef', 'c-clef', 'f-clef']]

    ##########################################################################
    return cropobjects


###############################################################################


def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-a', '--annot', action='store', required=True,
                        help='The annotation file for which the staffline and staff'
                             ' CropObject relationships should be added.')
    parser.add_argument('-e', '--export', action='store',
                        help='A filename to which the output CropObjectList'
                             ' should be saved. If not given, will print to'
                             ' stdout.')

    parser.add_argument('-t', '--notehead_staffspace_threshold', action='store', type=float,
                        default=0.2,
                        help='If the ratio of the smaller to the larger lobe w.r.t.'
                             ' an overlapped staffline is lower than this, we consider'
                             ' the notehead to belong to the adjacent staffspace.')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on INFO messages.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on DEBUG messages.')

    return parser


def main(args):
    logging.info('Starting main...')
    _start_time = time.clock()

    ##########################################################################
    logging.info('Import the CropObject list')
    if not os.path.isfile(args.annot):
        raise ValueError('Annotation file {0} not found!'
                         ''.format(args.annot))
    cropobjects = parse_cropobject_list(args.annot)

    output_cropobjects = add_staff_relationships(
        cropobjects,
        notehead_staffspace_threshold=args.notehead_staffspace_threshold)

    ##########################################################################
    logging.info('Export the combined list.')
    cropobject_string = export_cropobject_list(output_cropobjects)

    if args.export is not None:
        with open(args.export, 'w') as hdl:
            hdl.write(cropobject_string)
    else:
        print(cropobject_string)

    _end_time = time.clock()
    logging.info('add_staff_reationships.py done in {0:.3f} s'
                 ''.format(_end_time - _start_time))


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main(args)
