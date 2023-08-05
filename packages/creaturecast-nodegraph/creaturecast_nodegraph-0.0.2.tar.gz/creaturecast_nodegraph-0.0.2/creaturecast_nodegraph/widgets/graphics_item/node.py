"""Node classes."""

import uuid
import PySignal as psg
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

import creaturecast_nodegraph.services.get_image as gmg
import creaturecast_nodegraph.services.thread_worker as twk
import creaturecast_nodegraph.media as med


class Node(QGraphicsItem):
    """A Node is a container for a header and 0-n Knobs.

    It can be created, removed and modified by the user in the UI.
    """
    def __init__(self, node, **kwargs):
        super(Node, self).__init__(**kwargs)
        self.node = node
        self.joints = node.nodes.get('joints', [])
        self.default_pixmap = QPixmap(med.get_icon_path('animal_fly'))
        # This unique id is useful for serialization/reconstruction.
        self.uuid = str(uuid.uuid4())

        self.header = None

        self.x = 0
        self.y = 0
        self.margin = 6
        self.spacing = 2
        self.width = 200
        self.height = 45
        self.header_height = 45
        self.plug_height = 26
        self.button_size = self.header_height - (self.margin * 2)
        self.button_margin = 8
        self.expanded_state = 0
        self.header_font = QFont('arial', 12, True)
        self.joint_font = QFont('arial', 11, False)
        self.text_margin = 3
        self.text_height = 20
        self.pixmap = None
        #self.header_font.setLetterSpacing(QFont.PercentageSpacing, 96)

        self.bounding_margin = 5

        self.fill_color = QColor(115, 115, 115, 210)
        self.header_color = QColor(140, 140, 140, 220)
        self.plug_color = QColor(105, 105, 105, 200)
        self.text_color = QColor(204, 204, 204)
        self.out_plug_color = QColor(180, 120, 120)

        self.fill_brush = QBrush(self.fill_color)
        self.thin_black_pen = QPen(QColor(85, 85, 85))
        self.thin_black_pen.setWidth(2)


        # General configuration.
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.setCursor(Qt.SizeAllCursor)

        self.setAcceptHoverEvents(True)
        self.setAcceptTouchEvents(True)
        self.setAcceptDrops(True)

        self.expand_button = ExpandButton()
        self.expand_button.h = self.button_size
        self.expand_button.w = self.button_size
        self.expand_button.x = self.width - self.button_size - self.button_margin
        self.expand_button.y = self.button_margin

        self.expand_button.setParentItem(self)
        self.expand_button.expanded.connect(self.set_expanded)

        self.plugs = []
        self.get_pixmap()

    def set_expanded(self, mode):

        self.delete_plugs()

        if mode == 0:
            self.height = self.header_height
        if mode == 2:
            joints = [x for x in self.node.nodes['joints']]

            self.height = self.header_height + (self.plug_height * (len(joints) + 1))

            matrix_plug = GraphPlug(self, '  matrix')
            matrix_plug.horizontal_alignment = Qt.AlignLeft

            matrix_plug.setParentItem(self)
            self.plugs.append(matrix_plug)

            for i, joint in enumerate(joints):
                new_plug = GraphPlug(self, 'joint_%s  ' % i)
                new_plug.setParentItem(self)
                self.plugs.append(new_plug)

        self.prepareGeometryChange()

        self.update()

    def boundingRect(self):
        rect = QRect(
            self.x - self.bounding_margin,
            self.y - self.text_height - self.bounding_margin,
            self.width + (self.bounding_margin * 2),
            self.height + self.text_height + (self.bounding_margin * 2) + 9
        )


        return rect

    def addHeader(self, header):
        """Assign the given header and adjust the Node's size for it."""
        self.header = header
        header.setPos(self.pos())
        header.setParentItem(self)
        self.updateSizeForChildren()

    def removeKnob(self, knob):
        """Remove the Knob reference to this node and resize."""
        knob.setParentItem(None)
        self.updateSizeForChildren()

    def paint(self, painter, option, widget):

        header_rectangle = QRect(
            QPoint(0, 0),
            QPoint(
                self.width,
                self.height + 9
            )
        )

        painter.setBrush(self.fill_brush)
        painter.setPen(self.thin_black_pen)
        painter.drawRoundedRect(header_rectangle, 7, 7)
        pixmap_rectangle = QRect(
            QPoint(
                self.margin,
                self.margin
            ),
            QPoint(
                self.header_height - self.margin,
                self.header_height - self.margin
            )
        )

        if self.pixmap:
            painter.drawPixmap(
                pixmap_rectangle,
                self.pixmap
            )

        text_rectangle = QRect(
            QPoint(
                self.text_margin,
                self.text_height * -1
            ),
            QPoint(
                self.width,
                self.text_margin * -1
            )
        )

        painter.setPen(QPen(self.text_color))
        painter.setFont(self.header_font)
        painter.drawText(
            text_rectangle,
            Qt.AlignBottom | Qt.AlignLeft,
            self.node.data['name']
        )




        '''
        header_rectangle = QRect(
                QPoint(-1, (self.icon_size) + self.margin),
                QPoint((self.icon_size) + (self.margin * 2), (self.icon_size)+ self.margin + self.header_height)
        )

        #plugs_rectangle = QRect(
         #       QPoint(0, (self.icon_size) + self.margin + self.header_height),
         #       self.boundingRect().bottomRight()
        #)



        painter.setBrush(QBrush(self.header_color))

        painter.drawRoundedRect(header_rectangle, 0, 0)

        painter.setBrush(QBrush(self.plug_color))

        #painter.drawRoundedRect(plugs_rectangle, 0, 0)

        painter.setPen(QPen(self.text_color))
        painter.setFont(self.header_font)
        painter.drawText(
            header_rectangle,
            Qt.AlignTop | Qt.AlignHCenter,
            self.node.data['root_name']
        )

        self.paint_plug(painter, 0, '   matrix', allignment=Qt.AlignLeft)



    '''

    def get_pixmap(self):


        if self.pixmap:
            return self.pixmap
        else:
            self.pixmap = self.default_pixmap
            self.worker = twk.FunctionWorker(gmg.get_image, self.node.data['icon'])
            self.thread = QThread()
            self.thread.start()
            self.worker.moveToThread(self.thread)
            self.worker.start.connect(self.worker.run)
            self.worker.data.connect(self.update_pixmap)
            self.worker.end.connect(self.thread.terminate)
            self.worker.start.emit()

    def update_pixmap(self, path):
        self.pixmap = QPixmap(path)
        self.update()

    def delete_plugs(self):

        for plug in self.plugs:
            plug.destroy()
        self.plugs = []

    def paint_plug(self, painter, i, name, allignment=Qt.AlignRight):



        painter.setBrush(QBrush(self.plug_color))
        painter.setPen(QPen(Qt.NoPen))

        if i % 2 == 0:
            plug_rectangle = QRect(
                QPoint(1, plug_top),
                QPoint(self.width-1, plug_bottom)
            )

            painter.drawRoundedRect(plug_rectangle, 0, 0)

        '''
        plug_radius = self.plug_height * 0.3

        if allignment == Qt.AlignRight:
            plug_point = QPoint(
                self.icon_size + (self.margin * 2),
                self.icon_size + self.margin + self.header_height + (self.spacing * (i + 1)) + (self.plug_height * (i + 1)) - (self.plug_height * 0.5)
            )

        else:
            plug_point = QPoint(
                0,
                self.icon_size + self.margin + self.header_height + (self.spacing * (i + 1)) + (self.plug_height * (i + 1)) - (self.plug_height * 0.5)
            )


        painter.setPen(self.thin_grey_pen)
        painter.setBrush(QBrush(self.plug_color))


        painter.setBrush(QBrush(self.out_plug_color))
        painter.drawEllipse(plug_point, 5, 5)

        painter.setPen(QPen(self.text_color))
        painter.setFont(self.joint_font)
        painter.drawText(
            plug_rectangle,
            Qt.AlignTop | allignment,
            name
        )
        '''
    def mouseMoveEvent(self, event):
        """Update selected item's (and children's) positions as needed.

        We assume here that only Nodes can be selected.

        We cannot just update our own childItems, since we are using
        RubberBandDrag, and that would lead to otherwise e.g. Edges
        visually lose their connection until an attached Node is moved
        individually.
        """
        nodes = self.scene().selectedItems()

        super(Node, self).mouseMoveEvent(event)

    def destroy(self):
        """Remove this Node, its Header, Knobs and connected Edges."""
        print("destroy node:", self)
        self.header.destroy()
        for knob in self.knobs():
            knob.destroy()

        scene = self.scene()
        scene.removeItem(self)
        del self


class ExpandButton(QGraphicsObject):

    expanded = Signal(int)

    def __init__(self, **kwargs):
        super(ExpandButton, self).__init__(**kwargs)
        self.x = 0
        self.y = 0
        self.w = 10
        self.h = 10

        self.margin = 5
        self.label_color = QColor(10, 10, 10)
        self.fill_color = QColor(0, 0, 0, 0)
        self.highlight_color = QColor(190, 190, 190)
        self._old_bar_color = QColor(130, 130, 130)
        self.bar_color = QColor(145, 145, 145)
        self.bar_alt_color = QColor(122, 122, 122)
        self.bar_alt_hilight_color = QColor(150, 150, 150)

        self.setAcceptHoverEvents(True)

        self.expand_mode = 1
        self.bar_spacing = 3
        self.bar_height = 7

        self.thin_grey_pen = QPen(QColor(204, 204, 204, 200))
        self.thin_grey_pen.setWidth(0.5)

    def node(self):
        return self.parentItem()

    def boundingRect(self):
        rect = QRect(self.x, self.y, self.w, self.h)
        return rect

    def highlight(self, toggle):

        if toggle:
            self._old_fill_color = self.bar_color
            self.bar_color = self.highlight_color
        else:
            self.bar_color = self._old_fill_color

    def paint(self, painter, option, widget):

        bbox = self.boundingRect()

        bar_count = self.expand_mode + 1

        painter.setBrush(QBrush(self.bar_color))
        painter.setPen(QPen(Qt.NoPen))

        for i in range(3):
            bar_rectangle = QRect(
                QPoint(bbox.topLeft().x(), (self.bar_spacing * i) + (self.bar_height * i) + bbox.top()),
                QPoint(bbox.bottomRight().x(), (self.bar_spacing * i) + (self.bar_height * (i+1)) + bbox.top())
            )

            if i > bar_count-1:
                painter.setBrush(self.bar_alt_color)

            painter.drawRoundedRect(bar_rectangle, 2, 2)

    def hoverEnterEvent(self, event):
        self.highlight(True)
        super(ExpandButton, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.highlight(False)
        super(ExpandButton, self).hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.expand_mode == 2:
                self.expand_mode = 0
            else:
                self.expand_mode += 1
            self.expanded.emit(self.expand_mode)
            self.update()
            return

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    def destroy(self):

        del self





class GraphPlug(QGraphicsObject):

    def __init__(self, node, name, **kwargs):
        super(GraphPlug, self).__init__(**kwargs)
        self.node = node
        self.name = name
        self.index = len(self.node.plugs)

        self.horizontal_alignment = Qt.AlignRight

        self.height = self.node.plug_height
        self.width = self.node.width - 2
        self.x = 1
        self.y = self.node.header_height + (self.height * self.index)

        self.joint_font = QFont('arial', 12, False)

        self.setAcceptHoverEvents(True)

        if self.index % 2 == 0:
            self.fill_brush = QBrush(QColor(120, 120, 120, 255))
        else:
            self.fill_brush = QBrush(Qt.NoBrush)

        self.no_pen = QPen(Qt.NoPen)
        self.pen = QPen(QColor(180, 180, 180))

    def node(self):
        return self.parentItem()

    def boundingRect(self):
        return QRect(QPoint(self.x, self.y), QPoint(self.x + self.width, self.y + self.height))

    def paint(self, painter, option, widget):

        bounding_rectangle = self.boundingRect()
        painter.setBrush(self.fill_brush)
        painter.setPen(self.no_pen)
        painter.drawRoundedRect(bounding_rectangle, 0, 0)

        painter.setFont(self.joint_font)
        painter.setPen(self.pen)

        painter.drawText(
            bounding_rectangle,
            Qt.AlignVCenter | self.horizontal_alignment,
            self.name
        )
    def destroy(self):
        self.setParentItem(None)
        del self



class GraphSocket(QGraphicsObject):

    def __init__(self, plug, **kwargs):
        super(GraphSocket, self).__init__(**kwargs)
        self.plug = plug
        self.radius = 5

    def boundingRect(self):
        return QRect()

    def paint(self, painter, option, widget):

        plug_point = QPoint(
            self.icon_size + (self.margin * 2),
            self.icon_size + self.margin + self.header_height + (self.spacing * (i + 1)) + (
                    self.plug_height * (i + 1)) - (self.plug_height * 0.5)
        )

        painter.setPen(self.thin_grey_pen)
        painter.setBrush(QBrush(self.plug_color))

        painter.setBrush(QBrush(self.out_plug_color))
        painter.drawEllipse(plug_point, 5, 5)

    def destroy(self):
        self.setParentItem(None)
        del self