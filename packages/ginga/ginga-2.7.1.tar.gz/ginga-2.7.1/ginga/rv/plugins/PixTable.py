#
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
"""
``PixTable`` provides a way to check or monitor the pixel values in
a region.

**Plugin Type: Local**

``PixTable`` is a local plugin, which means it is associated with a channel.
An instance can be opened for each channel.

**Basic Use**

In the most basic use, simply move the cursor around the channel
viewer; an array of pixel values will appear in the "Pixel Values"
display in the plugin UI.  The center value is highlighted, and this
corresponds to the value under the cursor.

You can choose a 3x3, 5x5, 7x7, or 9x9 grid from the left-most
combobox control.  It may help to adjust the "Font Size" control
to prevent having the array values cut off on the sides.  You can
also enlarge the plugin workspace to see more of the table.

.. note:: The order of the value table shown will not necessarily match to
          the channel viewer if the images is flipped, transposed, or rotated.

**Using Marks**

If you click in the channel viewer, it will set a mark.  There can
be any number of marks, and they are each noted with an "X"
annotated with a number.  When that mark is selected, it will only
show the values around the mark.  Simply change the mark control to
select a different mark to see the values around it.

The marks will stay in position even if a new image is loaded and
they will show the values for the new image.  In this way you can
monitor the area around a spot if the image is updating frequently.

If the "Pan to mark" checkbox is selected, then when you select a
different mark from the mark control, the channel viewer will pan to
that mark.  This can be useful to inspect the same spots in several
different images.

.. note:: If you change the mark control back to "None", then the pixel
          table will again update as you move the cursor around the viewer.

**Deleting Marks**

To delete a mark, select it in the mark control and then press the
button marked "Delete".  To delete all the marks, press the button
marked "Delete All".

**User Configuration**

"""
import numpy as np

from ginga.gw import Widgets, Viewers
from ginga import GingaPlugin, colors

__all__ = ['PixTable']


class PixTable(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):
        # superclass defines some variables for us, like logger
        super(PixTable, self).__init__(fv, fitsimage)

        self.layertag = 'pixtable-canvas'
        self.pan2mark = False

        prefs = self.fv.get_preferences()
        self.settings = prefs.create_category('plugin_PixTable')
        self.settings.add_defaults(fontsize=12,
                                   font='fixed')
        self.settings.load(onError='silent')

        self.dc = self.fv.get_draw_classes()
        canvas = self.dc.DrawingCanvas()
        canvas.set_callback('cursor-down', self.btndown_cb)
        canvas.set_callback('cursor-changed', self.cursor_cb)
        canvas.set_surface(self.fitsimage)
        self.canvas = canvas

        # For pixel table
        self.pixtbl_radius = 2
        self.txt_arr = None
        self.sum_arr = None
        self.sizes = [1, 2, 3, 4]
        self.maxdigits = 9
        self.fmt_cell = '{:> %d.%dg}' % (self.maxdigits - 1, self.maxdigits // 2)
        self.lastx = 0
        self.lasty = 0
        self.font = self.settings.get('font', 'fixed')
        self.fontsize = self.settings.get('fontsize', 12)
        self.fontsizes = [6, 8, 9, 10, 11, 12, 14, 16, 18, 24, 28, 32]
        self.pixview = None
        self._wd = 400
        self._ht = 300

        # For "marks" feature
        self.mark_radius = 10
        self.mark_style = 'cross'
        self.mark_color = 'purple'
        self.select_color = 'cyan'
        self.marks = ['None']
        self.mark_index = 0
        self.mark_selected = None

    def build_gui(self, container):
        top = Widgets.VBox()
        top.set_border_width(4)

        box, sw, orientation = Widgets.get_oriented_box(container)
        box.set_border_width(4)
        box.set_spacing(2)

        fr = Widgets.Frame("Pixel Values")

        # We just use a ginga widget to implement the pixtable
        pixview = Viewers.CanvasView(logger=self.logger)
        pixview.set_desired_size(self._wd, self._ht)
        bg = colors.lookup_color('#202030')
        pixview.set_bg(*bg)

        bd = pixview.get_bindings()
        bd.enable_zoom(True)
        bd.enable_pan(True)

        self.pixview = pixview
        self.pix_w = Viewers.GingaViewerWidget(pixview)
        fr.set_widget(self.pix_w)
        self.pix_w.resize(self._wd, self._ht)

        paned = Widgets.Splitter(orientation=orientation)
        paned.add_widget(fr)

        self._rebuild_table()

        btns = Widgets.HBox()
        btns.set_border_width(4)
        btns.set_spacing(4)

        cbox1 = Widgets.ComboBox()
        index = 0
        for i in self.sizes:
            j = 1 + i * 2
            name = "%dx%d" % (j, j)
            cbox1.append_text(name)
            index += 1
        index = self.sizes.index(self.pixtbl_radius)
        cbox1.set_index(index)
        cbox1.add_callback('activated', self.set_cutout_size_cb)
        cbox1.set_tooltip("Select size of pixel table")
        btns.add_widget(cbox1, stretch=0)

        # control for selecting a mark
        cbox2 = Widgets.ComboBox()
        for tag in self.marks:
            cbox2.append_text(tag)
        if self.mark_selected is None:
            cbox2.set_index(0)
        else:
            cbox2.show_text(self.mark_selected)
        cbox2.add_callback('activated', self.mark_select_cb)
        self.w.marks = cbox2
        cbox2.set_tooltip("Select a mark")
        #cbox2.setMinimumContentsLength(8)
        btns.add_widget(cbox2, stretch=0)

        btn1 = Widgets.Button("Delete")
        btn1.add_callback('activated', lambda w: self.clear_mark_cb())
        btn1.set_tooltip("Delete selected mark")
        btns.add_widget(btn1, stretch=0)

        btn2 = Widgets.Button("Delete All")
        btn2.add_callback('activated', lambda w: self.clear_all())
        btn2.set_tooltip("Clear all marks")
        btns.add_widget(btn2, stretch=0)
        btns.add_widget(Widgets.Label(''), stretch=1)

        vbox2 = Widgets.VBox()
        vbox2.add_widget(btns, stretch=0)

        btns = Widgets.HBox()
        btns.set_border_width(4)
        btns.set_spacing(4)

        btn3 = Widgets.CheckBox("Pan to mark")
        btn3.set_state(self.pan2mark)
        btn3.add_callback('activated', self.pan2mark_cb)
        btn3.set_tooltip("Pan follows selected mark")
        btns.add_widget(btn3)
        btns.add_widget(Widgets.Label(''), stretch=1)

        vbox2.add_widget(btns, stretch=0)

        captions = [
            ('Font size:', 'label', 'Font size', 'combobox'),
        ]
        w, b = Widgets.build_info(captions)
        self.w.update(b)
        vbox2.add_widget(w, stretch=0)

        b.font_size.set_tooltip("Set font size for pixel display")
        for size in self.fontsizes:
            b.font_size.append_text(str(size))
        b.font_size.show_text(str(self.fontsize))
        b.font_size.add_callback('activated', self.set_font_size_cb)

        vbox2.add_widget(Widgets.Label(''), stretch=1)
        box.add_widget(vbox2, stretch=1)

        ## spacer = Widgets.Label('')
        ## box.add_widget(spacer, stretch=1)

        paned.add_widget(sw)
        # hack to set a reasonable starting position for the splitter
        _sz = max(self._wd, self._ht)
        paned.set_sizes([_sz, _sz])

        top.add_widget(paned, stretch=1)

        btns = Widgets.HBox()
        btns.set_border_width(4)
        btns.set_spacing(4)

        btn = Widgets.Button("Close")
        btn.add_callback('activated', lambda w: self.close())
        btns.add_widget(btn)
        btn = Widgets.Button("Help")
        btn.add_callback('activated', lambda w: self.help())
        btns.add_widget(btn, stretch=0)
        btns.add_widget(Widgets.Label(''), stretch=1)

        top.add_widget(btns, stretch=0)
        container.add_widget(top, stretch=1)

    def select_mark(self, tag, pan=True):
        # deselect the current selected mark, if there is one
        if self.mark_selected is not None:
            try:
                obj = self.canvas.get_object_by_tag(self.mark_selected)
                obj.set_attr_all(color=self.mark_color)
            except Exception:
                # old object may have been deleted
                pass

        self.mark_selected = tag
        if tag is None:
            self.w.marks.show_text('None')
            self.canvas.redraw(whence=3)
            return

        self.w.marks.show_text(tag)
        obj = self.canvas.get_object_by_tag(tag)
        obj.set_attr_all(color=self.select_color)
        self.lastx = obj.objects[0].x
        self.lasty = obj.objects[0].y
        if self.pan2mark and pan:
            self.fitsimage.panset_xy(self.lastx, self.lasty)
        self.canvas.redraw(whence=3)

        self.redo()

    def mark_select_cb(self, w, index):
        tag = self.marks[index]
        if index == 0:
            tag = None
        self.select_mark(tag)

    def pan2mark_cb(self, w, val):
        self.pan2mark = val

    def clear_mark_cb(self):
        tag = self.mark_selected
        if tag is None:
            return
        self.canvas.delete_object_by_tag(tag)
        self.w.marks.delete_alpha(tag)
        self.marks.remove(tag)
        self.w.marks.set_index(0)
        self.mark_selected = None

    def clear_all(self):
        self.canvas.delete_all_objects()
        for name in self.marks:
            self.w.marks.delete_alpha(name)
        self.marks = ['None']
        self.w.marks.append_text('None')
        self.w.marks.set_index(0)
        self.mark_selected = None

    def set_font_size_cb(self, w, index):
        self.fontsize = self.fontsizes[index]
        self._rebuild_table()

    def plot(self, data, x1, y1, x2, y2, data_x, data_y, radius,
             maxv=9):

        # Because most FITS data is stored with lower Y indexes to
        # bottom
        data = np.flipud(data)

        width, height = self.fitsimage.get_dims(data)
        if self.txt_arr is None:
            return

        maxval = np.nanmax(data)
        minval = np.nanmin(data)
        avgval = np.average(data)
        fmt_cell = self.fmt_cell

        # can we do this with a np.vectorize() fn call and
        # speed things up?
        for i in range(width):
            for j in range(height):
                self.txt_arr[i][j].text = fmt_cell.format(data[i][j])

        ctr_txt = self.txt_arr[width // 2][height // 2]

        # append statistics line
        fmt_stat = "  Min: %s  Max: %s  Avg: %s" % (fmt_cell, fmt_cell,
                                                    fmt_cell)
        self.sum_arr[0].text = fmt_stat.format(minval, maxval, avgval)

        # update the pixtable
        self.pixview.panset_xy(ctr_txt.x, ctr_txt.y)
        #self.pixview.redraw(whence=3)

    def close(self):
        self.fv.stop_local_plugin(self.chname, str(self))
        return True

    def start(self):
        # insert layer if it is not already
        p_canvas = self.fitsimage.get_canvas()
        try:
            p_canvas.get_object_by_tag(self.layertag)

        except KeyError:
            # Add canvas layer
            p_canvas.add(self.canvas, tag=self.layertag)
        self.resume()

    def stop(self):
        # remove the canvas from the image
        self.canvas.ui_set_active(False)
        p_canvas = self.fitsimage.get_canvas()
        try:
            p_canvas.delete_object_by_tag(self.layertag)
        except Exception:
            pass
        self.pixview = None

    def pause(self):
        self.canvas.ui_set_active(False)

    def resume(self):
        # turn off any mode user may be in
        self.modes_off()

        self.canvas.ui_set_active(True)
        self.redo()

    def redo(self):
        if self.pixview is None:
            return
        # cut out and set the pixel table data
        image = self.fitsimage.get_image()

        if image is None:
            return

        # We report the value across the pixel, even though the coords
        # change halfway across the pixel
        data_x, data_y = int(self.lastx + 0.5), int(self.lasty + 0.5)

        # cutout image data
        data, x1, y1, x2, y2 = image.cutout_radius(data_x, data_y,
                                                   self.pixtbl_radius)
        self.fv.error_wrap(self.plot, data, x1, y1, x2, y2,
                           self.lastx, self.lasty,
                           self.pixtbl_radius, maxv=9)

    def _rebuild_table(self):
        canvas = self.pixview.get_canvas()
        canvas.delete_all_objects(redraw=False)

        Text = canvas.get_draw_class('text')
        ex_txt = Text(0, 0, text='5', fontsize=self.fontsize, font=self.font)
        font_wd, font_ht = self.fitsimage.renderer.get_dimensions(ex_txt)
        max_wd = self.maxdigits + 2
        crdmap = self.pixview.get_coordmap('window')

        rows = []
        objs = []
        max_x = 0
        for row in range(self.pixtbl_radius * 2 + 1):
            cols = []
            for col in range(self.pixtbl_radius * 2 + 1):
                col_wd = font_wd * max_wd
                x = col_wd * col + 4
                max_x = max(max_x, x + col_wd)
                y = font_ht * (row + 1) + 4

                color = 'lightgreen'
                if (row == col) and (row == self.pixtbl_radius):
                    color = 'pink'

                dx, dy = crdmap.to_data((x, y))
                text_obj = Text(dx, dy, text='', font=self.font,
                                color=color, fontsize=self.fontsize,
                                coord='data')
                objs.append(text_obj)
                cols.append(text_obj)

            rows.append(cols)

        self.txt_arr = np.array(rows)

        # add summary row(s)
        x = (font_wd + 2) + 4
        y += font_ht + 20
        dx, dy = crdmap.to_data((x, y))
        s1 = Text(dx, dy, text='', font=self.font,
                  color=color, fontsize=self.fontsize,
                  coord='data')
        objs.append(s1)
        self.sum_arr = np.array([s1])

        # add all of the text objects to the canvas as one large
        # compound object
        CompoundObject = canvas.get_draw_class('compoundobject')
        canvas.add(CompoundObject(*objs), redraw=False)

        # set limits for scrolling
        self.pixview.set_limits(((0, 0), (max_x, y)), coord='window')

    def set_cutout_size_cb(self, w, val):
        index = w.get_index()
        self.pixtbl_radius = self.sizes[index]
        self._rebuild_table()

    def cursor_cb(self, canvas, junk, data_x, data_y):
        if self.mark_selected is not None:
            return False
        if self.pixview is None:
            return

        self.lastx, self.lasty = data_x, data_y

        self.redo()
        return False

    def btndown_cb(self, canvas, event, data_x, data_y):
        self.add_mark(data_x, data_y)
        return True

    def add_mark(self, data_x, data_y, radius=None, color=None, style=None):
        if not radius:
            radius = self.mark_radius
        if not color:
            color = self.mark_color
        if not style:
            style = self.mark_style

        self.logger.debug("Setting mark at %d,%d" % (data_x, data_y))
        self.mark_index += 1
        tag = 'mark%d' % (self.mark_index)
        tag = self.canvas.add(self.dc.CompoundObject(
            self.dc.Point(data_x, data_y, self.mark_radius,
                          style=style, color=color,
                          linestyle='solid'),
            self.dc.Text(data_x + 10, data_y, "%d" % (self.mark_index),
                         color=color)),
            tag=tag)
        self.marks.append(tag)
        self.w.marks.append_text(tag)
        self.select_mark(tag, pan=False)

    def __str__(self):
        return 'pixtable'


# Append module docstring with config doc for auto insert by Sphinx.
from ginga.util.toolbox import generate_cfg_example  # noqa
if __doc__ is not None:
    __doc__ += generate_cfg_example('plugin_PixTable', package='ginga')

# END
