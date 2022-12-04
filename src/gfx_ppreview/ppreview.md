# gfx_ppreview

20221126..1201

## 20221127:

Resume: Сделать *полностью* резиновый дизайно *сейчас* сложно (freeze).
Поэтому делать 2 predefined designs (landscape/portrait) + IgnoreAspectRatio + небольшой запас для резины:

- Base: pure items
- Grid: hand made
- Size: 748×1130 (A4-10mm @ 100 dpi)

### ToDo:
- [ ] Multisig bars:
  + [ ] Multisig
  + [ ] Bar v-gaps/pads (yz!)
- [ ] Options:
  + [ ] FIXME: QTableWidget: graphs too small
  + [ ] FIXME: Render: not call after 2+ `__init__()`
  + [ ] TODO: RectTextItem: rm rect (use .shear())
  + [ ] Try: transform
  + [ ] PyQt6 complain

### Done:
- [x] Label cut
- [x] ~Try Layouts:~
  + [x] ~Grid~ (QGraphicsGridLayout; no samples)
  + [x] ~Linear~ (QGraphicsLinearLayout; `animation/states/states.py`)
  + [x] ~Anchor~ (QGraphicsAnchorLayout; `graphicsview/anchorlayout.py`)
- [x] View:
  + [x] Real sizes
  + [x] Var heights
  + [x] Landscape/Portrait (row height, graph width/step)
  + [x] Resize to original
  + [x] ~ViewWindow~ PlotView as ViewWindow
  + [x] View on/off
  + [x] Bottom bar:
    * [x] rect
    * [x] text[]:
      + [x] top-center
      + [x] Fixed: clip
  + [x] Hotkeys
  + [x] Canvas (exact A4):
    - [x] Base
    - [x] Tics
  + [x] TODO: Analog/Binary graphs
  + [x] TODO: initial autofill DATA
  + [ ] Paging:
    + [x] split data
    + [x] mk scenes
    + [x] set to 1st
    + [x] switch pages (hotkey/menu)
    + [x] HeaderItem width: clip (Warn: with parent rect only)
  + [x] Text clippath (by parent only)
  + [x] Rm linear layout
  + [x] ^P/^L => ^O (switch orientation)
- [x] Print:
  - [x] Fixed: Default orientation
  - [x] Fixed: Skip last newPage()
  - [x] Fixed: text too small
  - [x] Done: Tmp render
- [x] Multisig bars:
  + [x] Data classed
  + [x] Y=0 line (signal, tmp)
  + [x] Filled B-sig
  + [x] V-shifted A-sig
- Options:
  + [x] MW.toolbar
  + [x] Fixed: View/Print: signals too high (overlap bottom)

## RTFM:

- QSplineSeries
- [spline](https://www.toptal.com/c-plus-plus/rounded-corners-bezier-curves-qpainter)
- [disable transform](https://stackoverflow.com/questions/1222914/qgraphicsview-and-qgraphicsitem-don%C2%B4t-scale-item-when-scaling-the-view-rect)
- [Scene border](https://www.qtcentre.org/threads/13814-how-to-enable-borders-in-QGraphicsScene)
- [Tic align](https://www.qtcentre.org/threads/51168-QGraphicsTextItem-center-based-coordinates)
