# Wall Slot Generator — Fusion 360 Add-in

Generates parametric slot-wall panels from just three inputs: wall width, height
and border width. The add-in calculates optimal slot size, spacing, and count
automatically. Supports two designs and live pattern preview.

---

## Requirements

- Autodesk Fusion 360 (2021 or later)
- macOS or Windows

---

## Installation

### Step 1 — Copy the folder

Copy the entire `wall_slots` folder (not just its contents) into your Fusion 360
add-ins directory:

**macOS**
```
~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/
```

**Windows**
```
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\
```

After copying, the structure should look like this:

```
AddIns/
└── wall_slots/
    ├── wall_slots.py
    ├── wall_slots.manifest
    ├── palette.html
    ├── icon.svg
    └── README.md
```

### Step 2 — Load in Fusion 360

1. Open Fusion 360
2. Go to **Tools → Scripts and Add-Ins** (or press **Shift+S**)
3. Click the **Add-Ins** tab
4. Find **wall_slots** in the list (click the refresh ⟳ button if it doesn't appear)
5. Check **Run on Startup**
6. Click **Run**

This adds a **Wall Slot Generator** button to the **Add-Ins** menu in the
**Design** workspace toolbar. You only do this once.

---

## Usage

1. Open a design and switch to the **Design** workspace
2. Open **Add-Ins** in the toolbar and click **Wall Slot Generator**
3. Enter **Wall width**, **Height**, **Thickness** and **Border width** in mm
4. Choose a **design pattern**:
   - **Design 1** — main rows with inter-row [small · large · small] triplets
   - **Design 2** — brick-offset rows, with optional half-slots at row ends
5. The pattern preview updates live as you type
6. Click **Generate wall** — the wall is created as a new component
7. To change parameters: adjust the values and click Generate again.
   The previous wall is replaced automatically.

Close the panel any time. Click **Wall Slot Generator** in **Add-Ins** to open
it again. You do not need to stop and start the add-in.

---

## Updating

To install a new version, replace the files in the `wall_slots` folder and
restart Fusion 360. With **Run on Startup** checked, the toolbar button is
back when Fusion opens. To reload without restarting, use **Shift+S**, select
**wall_slots**, then click **Stop** and **Run**.

---

## Folder contents

| File | Purpose |
|---|---|
| `wall_slots.py` | Add-in logic, solvers, Fusion 360 API calls |
| `wall_slots.manifest` | Add-in metadata (required by Fusion) |
| `palette.html` | Floating panel UI with live preview |
| `icon.svg` | Add-in icon (scalable) |
| `README.md` | This file |
