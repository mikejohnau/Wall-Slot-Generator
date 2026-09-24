# Wall Slot Generator — Usage Guide

## Overview

Wall Slot Generator creates parametric slot-wall panels directly inside Fusion 360.
You provide three dimensions and the add-in handles everything else — slot size,
spacing, row and column count — producing a fully cut solid body in a single click.
The result drops straight into your existing design as a named component, ready for
CAM, rendering, assembly, or export.

---

## Typical workflow

```
Open a Fusion 360 design  (Design workspace)
        ↓
Click Wall Slot Generator  (toolbar → Add-Ins → Wall Slot Generator)
        ↓
Enter wall dimensions and choose a pattern
        ↓
Click Generate
        ↓
Wall component appears in your design tree
        ↓
Apply materials, add to assembly, export for CAM or 3D print
        ↓
Need changes? Adjust values and click Generate again — previous wall is replaced
```

---

## Step-by-step panel walkthrough

### 1. Open the panel

In the **Design** workspace, open **Add-Ins** in the toolbar and click
**Wall Slot Generator**. The panel opens floating on screen. Close it whenever
you like; click the same button to open it again. It remembers your last
values, so the next session starts where you left off.

The first time you install the add-in, enable it once so that button exists:

1. Go to **Tools → Scripts and Add-Ins** (or press **Shift+S**)
2. Open the **Add-Ins** tab and select **wall_slots**
3. Check **Run on Startup**, then click **Run**

After that, Fusion loads the button at startup. You do not stop and start the
add-in to open the panel.

### Subscription

Wall Slot Generator is sold on the Autodesk App Store as a monthly or yearly
subscription. Opening the panel asks Autodesk, once per Fusion session, whether
the signed-in account's subscription is active. **Generate wall** stays
available while it is.

If that check fails because you are offline, a subscription confirmed in the
last 7 days still allows generation. After that, connect to the internet and
choose **Check again** in the panel. **Subscribe** opens the App Store listing.

### 2. Set your wall dimensions

| Field | What to enter |
|---|---|
| **Width** | Overall wall width in mm |
| **Height** | Overall wall height in mm |
| **Thickness** | Wall body depth in mm — typically 5–18mm depending on material |
| **Border width** | Distance from the wall edge to the inner edge of the border frame (set to 0 for no border) |

The slot field is automatically centred within the border on all four sides.

### 3. Choose a pattern

**Design 1 — Rows + inter-rows**
Full-width rows of large stadium slots, with a secondary row of smaller slots
nestled between each pair of main rows. The inter-row slots follow a
[small · large · small] triplet pattern that aligns precisely with the spacing
of the rows above and below. Best for high-density tool walls, display panels,
and any application where maximum hook or accessory points are needed.

**Design 2 — Brick offset**
Rows of identical large slots offset by half a pitch on alternate rows, creating
a classic running-bond pattern. Optionally enables **half-slots** — slots with
one flat (square) end — at the ends of offset rows, filling the space cleanly
against the border. Better suited to applications where a regular repeating
pattern matters visually, such as architectural screening or cabinet backs.

### 4. Set slot spacing

The **Slot spacing** slider controls packing density across a continuous range:

| Position | Character |
|---|---|
| **Open** (left) | Large gaps, fewer slots — airy, decorative |
| **Loose** (≈57%) | Classic slatwall proportions — the standard retail/workshop ratio |
| **Tight** (≈86%) | Close-packed — maximum hooks per panel |
| **Dense** (right) | Very tight — primarily for small panels or decorative screens |

The calculated layout panel updates live as you drag, showing exact slot
dimensions, gap sizes, and total slot count before you commit.

### 5. Read the calculated layout

Before clicking Generate, check the calculated layout panel:

```
6 columns × 3 rows — 18 main + 12 inter-row = 30 slots total

Main slot   32.0 × 8.0 mm  (straight 24.0 mm, r 4.0 mm)
Small slot  14.0 × 8.0 mm  (straight 6.0 mm)

H gap 4.0 mm  ·  V gap 3.0 mm
```

This confirms what Fusion will generate. If the slot count or size doesn't suit
your application, adjust dimensions or density and the preview updates instantly.

### 6. Generate

Click **Generate wall**. Fusion creates a component named **Wall Slot Panel**
containing the wall body with all slots cut through. The status bar confirms
success, or shows an error message if something went wrong.

### 7. Iterate

To change any parameter — dimensions, pattern, density — simply adjust the
values and click Generate again. The previous wall component is deleted and
replaced automatically. No undo step needed.

---

## Where the generated component fits in your design

The wall appears in the **Fusion 360 browser** (left panel) under:

```
Components
  └── Wall Slot Panel
        ├── Wall outline (sketch)
        ├── Slot profiles (sketch)
        ├── Extrude1 (wall body)
        └── Extrude2 (slot cut)
```

From here it behaves like any other Fusion component:

### Assembly
Drag the component into a larger assembly. Use **Joint** or **As-Built Joint**
to position it relative to a cabinet body, workbench frame, or wall mounting
system. The border creates a natural reference edge for flush-mounting.

### Applying materials and appearances
Right-click the body → **Appearance** to assign timber, MDF, aluminium, steel,
or any Fusion material. The slot profile reads correctly under all standard
render materials.

### CAM (machining)
Switch to the **Manufacture** workspace. The slot profiles are simple 2D pocket
and contour operations — compatible with all standard CAM strategies. The
through-cut extrusion means Fusion recognises slot walls and floors correctly
for toolpath generation. Recommended workflow:
- Use **2D Pocket** for slot interiors (router bit, down-cut spiral)
- Use **2D Contour** for the outer wall profile
- Set stock to match your sheet material thickness

### 3D printing
Export the body as STL or 3MF via **File → Export**. The 4:1 slot aspect ratio
and minimum gap sizes (≥ 1mm at dense packing) are chosen to remain printable
on FDM machines. For best results orient the wall flat on the build plate with
slots cutting vertically through the Z axis.

### DXF export for laser / CNC routing
Use **File → Export → DXF** from the sketch workspace, or use the **Drawings**
workspace to produce a flat pattern. The slot sketch is clean closed-profile
geometry — no gaps or overlapping curves — which imports directly into most
CAM and laser software without cleanup.

---

## Common applications

| Application | Recommended settings |
|---|---|
| Workshop tool wall | Design 1, Loose–Tight, 12–18mm thick |
| Retail display panel | Design 1, Loose, 15–18mm thick MDF |
| Cabinet back panel | Design 2, Loose, 6–9mm thick ply |
| Architectural screen | Design 2 + half-slots, Open–Loose, any thickness |
| 3D-printed organiser | Design 1 or 2, Tight, 4–6mm thick |
| Acoustic diffuser | Design 1, Loose, depth varies by frequency target |
| Laser-cut decorative insert | Design 2 + half-slots, Open, 3–6mm |

---

## Tips

**Matching standard slatwall accessories**
Standard slatwall hooks fit a 25.4mm × 9.5mm slot pitch. To target this, set
wall width to a multiple of 25.4mm and use the Loose preset — the solver will
find slot dimensions close to spec. Fine-tune with the density slider.

**Border as a mounting flange**
Set border width to 20–30mm and wall thickness to 18mm+ to create a sturdy
perimeter frame suitable for screw-mounting directly to a wall or cabinet side.

**Multiple panels in one design**
Generate a panel, rename the component (right-click → Rename) to something
like "Panel A", then click **Wall Slot Generator** again and generate a second
panel with different dimensions. Each generation replaces the component named
**Wall Slot Panel** only — previously renamed components are left untouched.

**Using the panel as a cut body**
After generating, use **Modify → Combine** with Cut operation to subtract the
slot pattern from a separate solid body (for example, a thicker cabinet door).
This lets you control the wall geometry independently from the slot depth.
