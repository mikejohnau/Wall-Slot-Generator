# wall_slots.py  —  Fusion 360 palette add-in  v1.1.0
#
# Files required in the same folder:
#   wall_slots.py  /  wall_slots.manifest  /  palette.html
# ─────────────────────────────────────────────────────────────────────────────

import adsk.core, adsk.fusion, adsk.cam
import traceback, os, json, math, time, webbrowser, urllib.parse, urllib.request

_handlers  = []
_PAL_ID    = 'wallSlotGen'
_CMD_ID    = 'wallSlotGenCmd'
_PANEL_ID  = 'SolidScriptsAddinsPanel'
_OWN_PANEL = 'WallSlotGenPanel'
_COMP_NAME = 'Wall Slot Panel'
_ATTR_GRP  = 'WallSlotGen'

# ── Slot-spacing formula ──────────────────────────────────────────────────────
# h = 0.25 → 0.03125 linearly (d=0 open, d=57 Loose, d=86 Tight, d=100 dense)
# v = h × 0.75   small_full = sf×(1-h)/2  (fills [S·L·S] gap exactly)

def _density_to_pack(density):
    h = 0.25 - (0.25 - 0.03125) * float(density) / 100.0
    return dict(h=h, v=h * 0.75, s=0.25)


_DEFAULTS = dict(
    wall_w=220, wall_h=60, wall_t=5, border_w=8,
    design=1, half_ends=0, density=57,
    orientation='horizontal',
    tile_cols=1, tile_rows=1, tile_gap=0
)

_des = None

# Autodesk App Store entitlement. Monthly and yearly plans both stay valid
# until the subscription expires; the API only reports IsValid.
_APP_ID = '6843713407655589746'
_STORE_URL = 'https://apps.autodesk.com/FUSION/en/Detail/Index?id=' + _APP_ID
_ENTITLEMENT_URL = 'https://apps.autodesk.com/webservices/checkentitlement'
_OFFLINE_GRACE_SEC = 7 * 24 * 60 * 60
_MSG_INVALID = (
    'This Autodesk account does not have an active Wall Slot Generator subscription. '
    'Subscribe monthly or yearly on the Autodesk App Store, then choose Check again.'
)
_MSG_OFFLINE = (
    'Wall Slot Generator could not reach Autodesk to confirm your subscription. '
    'Connect to the internet and choose Check again.'
)
_license = {'state': 'unknown', 'message': ''}
_session_checked = False


def _cache_path():
    return os.path.join(_script_dir(), 'entitlement_cache.json')


def _read_cache():
    try:
        with open(_cache_path(), encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def _write_cache(user_id, valid):
    try:
        with open(_cache_path(), 'w', encoding='utf-8') as f:
            json.dump({'user_id': user_id, 'valid': bool(valid), 'checked_at': time.time()}, f)
    except Exception:
        pass


def _offline_grant(user_id):
    cache = _read_cache()
    if not cache or not cache.get('valid'):
        return False
    if user_id and cache.get('user_id') != user_id:
        return False
    try:
        age = time.time() - float(cache.get('checked_at', 0))
    except Exception:
        return False
    return 0 <= age <= _OFFLINE_GRACE_SEC


def _set_license(state, message):
    _license['state'] = state
    _license['message'] = message


def _license_payload():
    return {
        'entitled': _license['state'] == 'valid',
        'license_message': _license['message'],
        'store_url': _STORE_URL,
    }


def _panel_payload():
    data = _load()
    data.update(_license_payload())
    return data


def _signed_in_user_id():
    app = adsk.core.Application.get()
    try:
        if app.isOffLine:
            return ''
        return app.userId or ''
    except Exception:
        return ''


def _ensure_entitlement(force=False):
    """Ask Autodesk once per session. A failed request can use a recent valid check."""
    global _session_checked
    if _session_checked and not force:
        return _license

    user_id = _signed_in_user_id()
    if not user_id:
        if _offline_grant(''):
            _set_license('valid', '')
        else:
            _set_license('offline', _MSG_OFFLINE)
        return _license

    try:
        query = urllib.parse.urlencode({'userid': user_id, 'appid': _APP_ID})
        req = urllib.request.Request(
            _ENTITLEMENT_URL + '?' + query,
            headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
        raw = payload.get('IsValid')
        valid = raw is True or str(raw).lower() == 'true'
        _session_checked = True
        _write_cache(user_id, valid)
        _set_license('valid' if valid else 'invalid', '' if valid else _MSG_INVALID)
    except Exception:
        if _offline_grant(user_id):
            _set_license('valid', '')
        else:
            _set_license('offline', _MSG_OFFLINE)
        _session_checked = True
    return _license


# ════════════════════════════════════════════════════════════════
#   ENTRY POINT
# ════════════════════════════════════════════════════════════════

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        _register_command(ui)
        adsk.autoTerminate(False)
    except:
        if ui: ui.messageBox('Startup error:\n\n' + traceback.format_exc())


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        _remove_command(ui)
        pal = ui.palettes.itemById(_PAL_ID)
        if pal: pal.deleteMe()
        _handlers.clear()
    except:
        pass


def _active_design():
    global _des
    _des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    return _des


def _script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _show_palette():
    ui = adsk.core.Application.get().userInterface
    _ensure_entitlement()
    _active_design()
    html_path = os.path.join(_script_dir(), 'palette.html')
    if not os.path.exists(html_path):
        ui.messageBox(f'palette.html not found:\n{html_path}')
        return

    pal = ui.palettes.itemById(_PAL_ID)
    if not pal:
        pal = ui.palettes.add(_PAL_ID, 'Wall Slot Generator',
                              html_path, True, True, True, 520, 640)
        if not pal:
            ui.messageBox('Failed to create palette.')
            return
        handler = _HTMLHandler()
        pal.incomingFromHTML.add(handler)
        _handlers.append(handler)
    pal.isVisible = True
    pal.sendInfoToHTML('init', json.dumps(_panel_payload()))


def _addins_panel(ui):
    workspace = ui.workspaces.itemById('FusionSolidEnvironment')
    if workspace:
        panel = workspace.toolbarPanels.itemById(_PANEL_ID)
        if panel:
            return panel
        tab = workspace.toolbarTabs.itemById('SolidTab')
        if tab:
            panel = tab.toolbarPanels.itemById(_OWN_PANEL)
            if not panel:
                panel = tab.toolbarPanels.add(_OWN_PANEL, 'Wall Slot', '', False)
            return panel
    return ui.allToolbarPanels.itemById(_PANEL_ID)


def _register_command(ui):
    _remove_command(ui)
    cmd_def = ui.commandDefinitions.addButtonDefinition(
        _CMD_ID,
        'Wall Slot Generator',
        'Open the Wall Slot Generator panel',
        os.path.join(_script_dir(), 'resources'))

    created = _CommandCreatedHandler()
    cmd_def.commandCreated.add(created)
    _handlers.append(created)

    panel = _addins_panel(ui)
    if not panel:
        ui.messageBox('Wall Slot Generator could not find a toolbar to add its button.')
        return
    control = panel.controls.itemById(_CMD_ID)
    if not control:
        control = panel.controls.addCommand(cmd_def)
    control.isPromotedByDefault = True
    control.isPromoted = True


def _remove_command(ui):
    workspace = ui.workspaces.itemById('FusionSolidEnvironment')
    if workspace:
        panel = workspace.toolbarPanels.itemById(_PANEL_ID)
        if panel:
            control = panel.controls.itemById(_CMD_ID)
            if control:
                control.deleteMe()
        tab = workspace.toolbarTabs.itemById('SolidTab')
        if tab:
            own = tab.toolbarPanels.itemById(_OWN_PANEL)
            if own:
                own.deleteMe()
    else:
        panel = ui.allToolbarPanels.itemById(_PANEL_ID)
        if panel:
            control = panel.controls.itemById(_CMD_ID)
            if control:
                control.deleteMe()
    cmd_def = ui.commandDefinitions.itemById(_CMD_ID)
    if cmd_def:
        cmd_def.deleteMe()


class _CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            cmd = adsk.core.Command.cast(args.command)
            execute = _CommandExecuteHandler()
            cmd.execute.add(execute)
            _handlers.append(execute)
        except:
            adsk.core.Application.get().userInterface.messageBox(
                'Wall Slot Generator error:\n\n' + traceback.format_exc())


class _CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            _show_palette()
        except:
            adsk.core.Application.get().userInterface.messageBox(
                'Wall Slot Generator error:\n\n' + traceback.format_exc())


# ════════════════════════════════════════════════════════════════
#   PERSIST
# ════════════════════════════════════════════════════════════════

def _load():
    p = dict(_DEFAULTS)
    if not _des: return p
    for k in p:
        a = _des.attributes.itemByName(_ATTR_GRP, k)
        if a:
            try:
                p[k] = float(a.value) if isinstance(p[k], (int, float)) else a.value
            except: pass
    return p

def _save(data):
    if not _des: return
    for k in _DEFAULTS:
        if k in data:
            _des.attributes.add(_ATTR_GRP, k, str(data[k]))


# ════════════════════════════════════════════════════════════════
#   HTML HANDLER
# ════════════════════════════════════════════════════════════════

class _HTMLHandler(adsk.core.HTMLEventHandler):
    def notify(self, args):
        args.returnData = json.dumps({'ok': False, 'error': 'Unknown error'})
        try:
            action = args.action
            data   = json.loads(args.data) if args.data else {}

            if action == 'openStore':
                webbrowser.open(_STORE_URL)
                args.returnData = json.dumps({'ok': True})

            elif action == 'recheck':
                _ensure_entitlement(force=True)
                payload = _license_payload()
                payload['ok'] = True
                args.returnData = json.dumps(payload)

            elif action == 'generate':
                _ensure_entitlement()
                if _license['state'] != 'valid':
                    args.returnData = json.dumps({'ok': False, 'error': _license['message']})
                    return
                if not _active_design():
                    args.returnData = json.dumps({'ok': False,
                        'error': 'Open a Fusion design, then generate the wall.'})
                    return
                _save(data)
                ww  = float(data['wall_w']);  wh = float(data['wall_h'])
                wt  = float(data['wall_t']);  bw = float(data['border_w'])
                design      = int(data.get('design', 1))
                half_ends   = bool(data.get('half_ends', False))
                density     = float(data.get('density', 57))
                orientation = data.get('orientation', 'horizontal')
                tile_cols   = max(1, int(data.get('tile_cols', 1)))
                tile_rows   = max(1, int(data.get('tile_rows', 1)))
                tile_gap    = float(data.get('tile_gap', 0))
                pack        = _density_to_pack(density)
                aw = ww - 2*bw; ah = wh - 2*bw
                vertical = (orientation == 'vertical')

                # Swap solver dimensions for vertical orientation
                sa, sb = (ah, aw) if vertical else (aw, ah)
                result = _solve1(sa, sb, pack) if design == 1 else _solve2(sa, sb, pack)
                if not result:
                    args.returnData = json.dumps({'ok': False,
                        'error': 'Cannot fit slots — try a larger wall, smaller border, or lower density.'})
                    return

                nc, nr, sf, hg, sh, vg = result
                _build(ww, wh, wt, bw, hg, vg, sf-sh, sh/2, nc, nr,
                       design=design, half_ends=half_ends,
                       vertical=vertical, tile_cols=tile_cols,
                       tile_rows=tile_rows, tile_gap=tile_gap)
                args.returnData = json.dumps({'ok': True})

            elif action == 'close':
                pal = adsk.core.Application.get().userInterface.palettes.itemById(_PAL_ID)
                if pal: pal.isVisible = False
                args.returnData = json.dumps({'ok': True})
            else:
                args.returnData = json.dumps({'ok': True})

        except Exception:
            err = traceback.format_exc()
            args.returnData = json.dumps({'ok': False, 'error': err})
            try:
                adsk.core.Application.get().userInterface.messageBox(
                    'Wall Slot Generator error:\n\n' + err)
            except:
                pass


# ════════════════════════════════════════════════════════════════
#   SOLVERS
# ════════════════════════════════════════════════════════════════

def _solve1(aw, ah, pack=None, min_sf=12):
    if pack is None: pack = _density_to_pack(57)
    h, v, s = pack['h'], pack['v'], pack['s']
    best = None; bs = -1; t = aw / 7
    for nr in range(1, 9):
        dh = 2*h + (2*nr-1)*s + (2*nr-2)*v
        if dh <= 0: continue
        sfh = ah / dh
        for nc in range(2, 32, 2):
            sf = min(aw / (nc*(1+h)+h), sfh)
            if sf < min_sf: continue
            hg=sf*h; sh=sf*s; vg=sf*v
            wu = nc*(sf+hg)+hg
            hu = 2*hg + (2*nr-1)*sh + (2*nr-2)*vg
            if wu > aw+0.01 or hu > ah+0.01: continue
            fw=wu/aw; fh=hu/ah
            sc = min(fw,fh)*0.4 + min(fw,fh)/max(fw,fh)*0.2 + 1/(1+abs(sf/t-1))*0.4
            if sc > bs: bs=sc; best=(nc,nr,sf,hg,sh,vg)
    return best

def _solve2(aw, ah, pack=None, min_sf=12):
    if pack is None: pack = _density_to_pack(57)
    h, v, s = pack['h'], pack['v'], pack['s']
    best = None; bs = -1; t = aw / 7
    for nr in range(1, 12):
        dh = 2*h + nr*s + (nr-1)*v
        if dh <= 0: continue
        sfh = ah / dh
        for nc in range(2, 32):
            sf = min(aw / (nc*(1+h)+h), sfh)
            if sf < min_sf: continue
            hg=sf*h; sh=sf*s; vg=sf*v
            wu = nc*(sf+hg)+hg
            hu = 2*hg + nr*sh + (nr-1)*vg
            if wu > aw+0.01 or hu > ah+0.01: continue
            fw=wu/aw; fh=hu/ah
            sc = min(fw,fh)*0.4 + min(fw,fh)/max(fw,fh)*0.2 + 1/(1+abs(sf/t-1))*0.4
            if sc > bs: bs=sc; best=(nc,nr,sf,hg,sh,vg)
    return best


# ════════════════════════════════════════════════════════════════
#   BUILDER
# ════════════════════════════════════════════════════════════════

def _build(wall_w, wall_h, wall_t, border_w,
           h_gap, v_gap, slot_len, slot_r,
           n_cols, n_rows, design=1, half_ends=False,
           vertical=False, tile_cols=1, tile_rows=1, tile_gap=0):

    root = _des.rootComponent

    # Remove previous wall component
    for o in [o for o in root.occurrences if o.component.name == _COMP_NAME]:
        o.deleteMe()

    # Create component — handles both Assembly and Part Design mode
    in_assembly = True
    try:
        occ  = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = occ.component
        comp.name = _COMP_NAME
    except RuntimeError as e:
        if any(k in str(e) for k in ('Part Design', 'one component', 'single component',
                                      'multiple component', 'only contain')):
            in_assembly = False
            comp = root
            _cleanup_root(root)
        else:
            raise

    sf         = slot_len + 2*slot_r
    slot_h     = 2*slot_r
    main_pitch = sf + h_gap
    area_w     = wall_w - 2*border_w
    area_h     = wall_h - 2*border_w

    if not vertical:
        visual_w = n_cols*(sf+h_gap) - h_gap
        h_used   = (2*h_gap + (2*n_rows-1)*slot_h + (2*n_rows-2)*v_gap if design == 1
                    else 2*h_gap + n_rows*slot_h + (n_rows-1)*v_gap)
        x0       = border_w + slot_r + (area_w - visual_w) / 2
        y0       = border_w + h_gap  + (area_h - h_used)  / 2
        tier     = 2*slot_h + 2*v_gap if design == 1 else slot_h + v_gap
    else:
        visual_h = n_cols*(sf+h_gap) - h_gap
        w_used   = (2*h_gap + (2*n_rows-1)*slot_h + (2*n_rows-2)*v_gap if design == 1
                    else 2*h_gap + n_rows*slot_h + (n_rows-1)*v_gap)
        x0       = border_w + h_gap  + (area_w - w_used)  / 2
        y0       = border_w + slot_r + (area_h - visual_h) / 2
        tier     = 2*slot_h + 2*v_gap if design == 1 else slot_h + v_gap

    # Wall solid
    sk_w = comp.sketches.add(comp.xYConstructionPlane)
    sk_w.name = 'Wall outline'
    sk_w.attributes.add(_ATTR_GRP, 'generated', '1')
    sk_w.sketchCurves.sketchLines.addTwoPointRectangle(_pt(0, 0), _pt(wall_w, wall_h))
    ei = comp.features.extrudeFeatures.createInput(
        sk_w.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(_cm(wall_t)))
    comp.features.extrudeFeatures.add(ei)

    # Slot sketch on offset plane — offset 0.1 mm ABOVE the wall top face.
    # Using the exact face height (_cm(wall_t)) makes the plane coincident with
    # the top face, causing Fusion to auto-project that face's edges into the
    # sketch and create a spurious large background profile. A tiny epsilon
    # above the face prevents this projection entirely.
    EPSILON_CM = 0.01   # 0.1 mm — above the top face, well within ThroughAll range
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(comp.xYConstructionPlane,
                   adsk.core.ValueInput.createByReal(_cm(wall_t) + EPSILON_CM))
    slot_plane = comp.constructionPlanes.add(pi)
    slot_plane.attributes.add(_ATTR_GRP, 'generated', '1')
    sk = comp.sketches.add(slot_plane)
    sk.name = 'Slot profiles'
    sk.attributes.add(_ATTR_GRP, 'generated', '1')

    if design == 1:
        _layout1(sk, x0, y0, n_cols, n_rows, slot_len, slot_r,
                 h_gap, v_gap, sf, slot_h, main_pitch, tier, vertical)
    else:
        _layout2(sk, x0, y0, n_cols, n_rows, slot_len, slot_r,
                 h_gap, v_gap, sf, slot_h, main_pitch, tier, half_ends,
                 area_w, area_h, border_w, vertical)

    # Extrude-cut slot profiles — filter by bounding-box area to exclude any
    # spurious large background region (which would invert the wall geometry).
    # The largest valid slot has bounding box ≈ sf × slot_h; anything much
    # bigger is the wall-boundary background region and must be skipped.
    max_slot_bb = _cm(sf) * _cm(slot_h) * 4.0   # generous 4× margin, in cm²
    profs = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        prof = sk.profiles.item(i)
        bb   = prof.boundingBox
        bb_area = ((bb.maxPoint.x - bb.minPoint.x) *
                   (bb.maxPoint.y - bb.minPoint.y))
        if bb_area <= max_slot_bb:
            profs.add(prof)
    if profs.count == 0:
        # Fallback: something went wrong with filtering — take all profiles
        for i in range(sk.profiles.count):
            profs.add(sk.profiles.item(i))
    ci = comp.features.extrudeFeatures.createInput(
        profs, adsk.fusion.FeatureOperations.CutFeatureOperation)
    ci.setOneSideExtent(
        adsk.fusion.ThroughAllExtentDefinition.create(),
        adsk.fusion.ExtentDirections.NegativeExtentDirection)
    comp.features.extrudeFeatures.add(ci)

    # Tiling (Assembly mode only)
    if in_assembly and (tile_cols > 1 or tile_rows > 1):
        for tr in range(tile_rows):
            for tc in range(tile_cols):
                if tr == 0 and tc == 0:
                    continue
                transform = adsk.core.Matrix3D.create()
                transform.translation = adsk.core.Vector3D.create(
                    _cm(tc * (wall_w + tile_gap)),
                    _cm(tr * (wall_h + tile_gap)),
                    0.0)
                root.occurrences.addExistingComponent(comp, transform)

    elif not in_assembly and (tile_cols > 1 or tile_rows > 1):
        adsk.core.Application.get().userInterface.messageBox(
            'Tiling requires an Assembly document.\n'
            'The wall was generated without tiling.\n\n'
            'Tip: Insert this component into an assembly, then use\n'
            'the Rectangular Pattern feature to create a tile array.')


def _cleanup_root(root):
    """Remove previously generated geometry from root component (Part Design mode)."""
    for sk in list(root.sketches):
        if sk.attributes.itemByName(_ATTR_GRP, 'generated'):
            sk.deleteMe()
    for cp in list(root.constructionPlanes):
        if cp.attributes.itemByName(_ATTR_GRP, 'generated'):
            cp.deleteMe()
    for body in list(root.bRepBodies):
        body.deleteMe()


# ════════════════════════════════════════════════════════════════
#   LAYOUT — Design 1
# ════════════════════════════════════════════════════════════════

def _layout1(sk, x0, y0, nc, nr, slot_len, slot_r,
             h_gap, v_gap, sf, slot_h, main_pitch, tier, vertical):
    small_full = sf * (1 - h_gap/sf) / 2  # = sf*(1-h)/2
    small_len  = small_full - 2*slot_r

    if not vertical:
        # ── Horizontal ──────────────────────────────────────────────────────
        for row in range(nr):
            y = y0 + row * tier
            for col in range(nc):
                _slot(sk, x0 + col*main_pitch, y, slot_len, slot_r)
        for irow in range(nr - 1):
            y = y0 + slot_h + v_gap + irow * tier
            for t in range(nc // 2):
                bx = x0 + t * 2 * main_pitch
                _slot(sk, bx,                            y, small_len, slot_r)
                _slot(sk, bx + small_full + h_gap,       y, slot_len,  slot_r)
                _slot(sk, bx + small_full + h_gap + sf + h_gap, y, small_len, slot_r)
    else:
        # ── Vertical ─────────────────────────────────────────────────────────
        # nc slots stack in Y, nr groups tile in X; tier = horizontal group width
        for grp in range(nr):
            x = x0 + grp * tier
            for col in range(nc):
                _slot_v(sk, x, y0 + col*main_pitch, slot_len, slot_r)
        for igrp in range(nr - 1):
            x = x0 + slot_h + v_gap + igrp * tier
            for t in range(nc // 2):
                by = y0 + t * 2 * main_pitch
                _slot_v(sk, x, by,                             small_len, slot_r)
                _slot_v(sk, x, by + small_full + h_gap,        slot_len,  slot_r)
                _slot_v(sk, x, by + small_full + h_gap + sf + h_gap, small_len, slot_r)


# ════════════════════════════════════════════════════════════════
#   LAYOUT — Design 2
# ════════════════════════════════════════════════════════════════

def _layout2(sk, x0, y0, nc, nr, slot_len, slot_r,
             h_gap, v_gap, sf, slot_h, main_pitch, tier,
             half_ends, area_w, area_h, border_w, vertical):
    half_w    = sf * (1 - h_gap/sf) / 2
    left_str  = half_w - slot_r
    right_str = half_w - 2*slot_r

    if not vertical:
        # ── Horizontal ──────────────────────────────────────────────────────
        vis_left  = x0 - slot_r
        visual_w  = nc*(sf+h_gap) - h_gap
        vis_right = vis_left + visual_w
        for row in range(nr):
            y = y0 + row * tier
            if row % 2 == 0:
                for col in range(nc):
                    _slot(sk, x0 + col*main_pitch, y, slot_len, slot_r)
            else:
                for col in range(nc - 1):
                    _slot(sk, x0 + main_pitch/2 + col*main_pitch, y, slot_len, slot_r)
                if half_ends:
                    if left_str > 0:
                        _slot_half(sk, vis_left, y, left_str, slot_r, flat_left=True)
                    right_x = vis_right - half_w + slot_r
                    if right_str > 0:
                        _slot_half(sk, right_x, y, right_str, slot_r, flat_left=False)
    else:
        # ── Vertical ─────────────────────────────────────────────────────────
        # nc slots stack in Y, nr groups tile in X
        vis_top    = y0 - slot_r
        visual_h   = nc*(sf+h_gap) - h_gap
        vis_bottom = vis_top + visual_h
        for grp in range(nr):
            x = x0 + grp * tier
            if grp % 2 == 0:
                for col in range(nc):
                    _slot_v(sk, x, y0 + col*main_pitch, slot_len, slot_r)
            else:
                for col in range(nc - 1):
                    _slot_v(sk, x, y0 + main_pitch/2 + col*main_pitch, slot_len, slot_r)
                if half_ends:
                    if left_str > 0:
                        _slot_half_v(sk, x, vis_top, left_str, slot_r, flat_top=True)
                    bot_y = vis_bottom - half_w + slot_r
                    if right_str > 0:
                        _slot_half_v(sk, x, bot_y, right_str, slot_r, flat_top=False)


# ════════════════════════════════════════════════════════════════
#   SLOT GEOMETRY
# ════════════════════════════════════════════════════════════════

def _slot(sketch, x, y, length, radius):
    """Horizontal stadium slot. x=left straight edge, y=bottom."""
    c = sketch.sketchCurves; r = radius
    c.sketchLines.addByTwoPoints(_pt(x,        y+2*r), _pt(x+length, y+2*r))
    c.sketchLines.addByTwoPoints(_pt(x,        y    ), _pt(x+length, y    ))
    c.sketchArcs.addByCenterStartSweep(_pt(x,        y+r), _pt(x,        y    ), -math.pi)
    c.sketchArcs.addByCenterStartSweep(_pt(x+length, y+r), _pt(x+length, y+2*r), -math.pi)

def _slot_v(sketch, x, y, length, radius):
    """Vertical stadium slot. x=left edge, y=top of straight portion."""
    c = sketch.sketchCurves; r = radius
    c.sketchLines.addByTwoPoints(_pt(x,     y),        _pt(x,     y+length))
    c.sketchLines.addByTwoPoints(_pt(x+2*r, y),        _pt(x+2*r, y+length))
    c.sketchArcs.addByCenterStartSweep(_pt(x+r, y),        _pt(x,     y),        -math.pi)
    c.sketchArcs.addByCenterStartSweep(_pt(x+r, y+length), _pt(x+2*r, y+length), -math.pi)

def _slot_half(sketch, x, y, length, radius, flat_left=True):
    """Horizontal half-slot: one flat end, one rounded end."""
    c = sketch.sketchCurves; r = radius; h = 2*r
    if flat_left:
        rx = x + length
        c.sketchLines.addByTwoPoints(_pt(x,  y  ), _pt(x,  y+h))
        c.sketchLines.addByTwoPoints(_pt(x,  y+h), _pt(rx, y+h))
        c.sketchLines.addByTwoPoints(_pt(x,  y  ), _pt(rx, y  ))
        c.sketchArcs.addByCenterStartSweep(_pt(rx, y+r), _pt(rx, y+h), -math.pi)
    else:
        rx = x + length + r
        c.sketchArcs.addByCenterStartSweep(_pt(x,  y+r), _pt(x,  y  ), -math.pi)
        c.sketchLines.addByTwoPoints(_pt(x,  y+h), _pt(rx, y+h))
        c.sketchLines.addByTwoPoints(_pt(x,  y  ), _pt(rx, y  ))
        c.sketchLines.addByTwoPoints(_pt(rx, y  ), _pt(rx, y+h))

def _slot_half_v(sketch, x, y, length, radius, flat_top=True):
    """Vertical half-slot: one flat end, one rounded end."""
    c = sketch.sketchCurves; r = radius; w = 2*r
    if flat_top:
        # flat top at y, round bottom
        ry = y + length
        c.sketchLines.addByTwoPoints(_pt(x,   y ), _pt(x+w, y ))
        c.sketchLines.addByTwoPoints(_pt(x,   y ), _pt(x,   ry))
        c.sketchLines.addByTwoPoints(_pt(x+w, y ), _pt(x+w, ry))
        c.sketchArcs.addByCenterStartSweep(_pt(x+r, ry), _pt(x+w, ry), -math.pi)
    else:
        # round bottom (lower Y), flat top (higher Y) — analogue of flat_left=False in _slot_half
        # flat must be at y + length + r  (NOT just y+length) to reach vis_boundary
        ry = y + length + r
        c.sketchArcs.addByCenterStartSweep(_pt(x+r, y ), _pt(x,   y ), -math.pi)
        c.sketchLines.addByTwoPoints(_pt(x,   y ), _pt(x,   ry))
        c.sketchLines.addByTwoPoints(_pt(x+w, y ), _pt(x+w, ry))
        c.sketchLines.addByTwoPoints(_pt(x,   ry), _pt(x+w, ry))

def _cm(v):    return v / 10.0
def _pt(x, y): return adsk.core.Point3D.create(_cm(x), _cm(y), 0.0)
