# gfx_ppreview

## RTFM:

- QSplineSeries
- [spline](https://www.toptal.com/c-plus-plus/rounded-corners-bezier-curves-qpainter)
- **QGraphicsGridLayout**
- [disable transform](https://stackoverflow.com/questions/1222914/qgraphicsview-and-qgraphicsitem-don%C2%B4t-scale-item-when-scaling-the-view-rect)
- [Scene border](https://www.qtcentre.org/threads/13814-how-to-enable-borders-in-QGraphicsScene)
- [Tic align](https://www.qtcentre.org/threads/51168-QGraphicsTextItem-center-based-coordinates)

## 20221126. Ideas (tmp.py):

- [x] TextItem: += rect (cut, border). Ok
- [x] find: TextItem setClip. Ok
- [x] ~try fill graph bg (== cut labels)~
- [ ] TextItem.paint: transform (freeze v-size (header, footer)
- [ ] GraphItem.paint: transform (resize, stretchfactor)
- [ ] Scene: add grid
- [ ] try anchor layout (fix header/footer)
- [ ] FIXME: remove margins of QGraphicsItem (see _pure)

## 20221127.

Сделать *полностью* резиновый дизайно *сейчас* сложно (freeze).
Поэтому делать 2 predefined дизайна (landscape/portrait) + IgnoreAspectRation + небольшой запас для резины:

- [ ] Основа - liners layout + pure items
- [ ] grid - hand made
- [ ] размеры - ~200×287, 2×3~ 748×1130

### ToDo:
- [ ] View:
  + [ ] FIXME: Bad PlotView size after L/P switching
  + [ ] FIXME: QTableWidget's graphs too small
  + [ ] TODO: text clippath
- [ ] Print
- [ ] TODO: MW.toolbar

### Done:
- [x] Label cut
- [x] ~Try Layouts:~
  + [x] ~Grid~ (QGraphicsGridLayout; no samples)
  + [x] ~Linear~ (QGraphicsLinearLayout; `animation/states/states.py`)
  + [x] ~Anchor~ (QGraphicsAnchorLayout; `graphicsview/anchorlayout.py`)
- [ ] View:
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
