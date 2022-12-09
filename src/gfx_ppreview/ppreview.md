# gfx_ppreview

20221126..1201 &ge; &le; &hellip; &times;

## 20221127:

Resume: Сделать *полностью* резиновый дизайно *сейчас* сложно (freeze).
Поэтому делать 2 predefined designs (landscape/portrait) + IgnoreAspectRatio + небольшой запас для резины:

- Base: pure items
- Grid: hand made
- Size: 748×1130 (A4-10mm @ 100 dpi)

### ToDo:
- [ ] Extra checkboxes (2nd line, ptrs)
- [ ] RectTextItem: rm rect (use .shear())
   *([sample](https://www.qtcentre.org/threads/57322-Adding-HTML-code-into-QTableWidget-cells))*
- [ ] Try: transform
- [ ] PyQt6 complain
- [ ] Tune geometry *(remember: X0=0, Xmax=width-1, line widths)*
- [ ] FIXME: Render: not call after 2+ `__init__()`
- [ ] Options
  + [ ] FIXME: QTableWidget: graphs too small  
     *(because transform includes pen width)*
  + [ ] TODO: A-sig: amplitude definition

### Done:
- Label cut
- ~Try Layouts:~
  + ~Grid~ (QGraphicsGridLayout; no samples)
  + ~Linear~ (QGraphicsLinearLayout; `animation/states/states.py`)
  + ~Anchor~ (QGraphicsAnchorLayout; `graphicsview/anchorlayout.py`)
- View:
  + Real sizes
  + Var heights
  + Landscape/Portrait (row height, graph width/step)
  + Resize to original
  + ~ViewWindow~ PlotView as ViewWindow
  + View on/off
  + Bottom bar:
    * rect
    * text[]:
      + top-center
      + Fixed: clip
  + Hotkeys
  + Canvas (exact A4):
    - Base
    - Tics
  + TODO: Analog/Binary graphs
  + TODO: initial autofill DATA
  + Paging:
    + split data
    + mk scenes
    + set to 1st
    + switch pages (hotkey/menu)
    + HeaderItem width: clip (Warn: with parent rect only)
  + Text clippath (by parent only)
  + Rm linear layout
  + ^P/^L => ^O (switch orientation)
- Print:
  - Fixed: Default orientation
  - Fixed: Skip last newPage()
  - Fixed: text too small
  - Done: Tmp render
- Multisig bars:
  + Data classed
  + Y=0 line (signal, tmp)
  + Filled B-sig
  + V-shifted A-sig
  + BarLabelItem
  + Through bar height
  + Fixed: BGraphItem: too thick
  + Fixed: BarGraphItem: Y0-line is debug-only for is_bool bars
  + Bar v-gaps
- Misc:
  + MW.toolbar
  + Fixed: View/Print: signals too high (overlap bottom)
  + Fixed: View/Print: bad y0 if max < 0 or min > 0
  + 2nd sig label line (optional)

## RTFM:

- QSplineSeries
- [spline](https://www.toptal.com/c-plus-plus/rounded-corners-bezier-curves-qpainter)
- [disable transform](https://stackoverflow.com/questions/1222914/qgraphicsview-and-qgraphicsitem-don%C2%B4t-scale-item-when-scaling-the-view-rect)
- [Scene border](https://www.qtcentre.org/threads/13814-how-to-enable-borders-in-QGraphicsScene)
- [Tic align](https://www.qtcentre.org/threads/51168-QGraphicsTextItem-center-based-coordinates)

## 20221204. Multisig

For each bar:

- for all signals: get min, max (bounding rect?)
- or boundingRect()?
- shift by -min()
- expand until given size
- normalize each signal (-1..+1):
  + B: as is
  + A: Ymin &le; 0, Ymax &ge; 0
- Y0=0
- on set_size() normalize all signals to 0..MAX

Ver.2:

- paint all signals normalized
- set_size():
  + shift on ...
  + resize by ordinar base
