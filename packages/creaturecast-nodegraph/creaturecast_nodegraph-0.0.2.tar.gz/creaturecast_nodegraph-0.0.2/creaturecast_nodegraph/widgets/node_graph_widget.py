from PySide.QtCore import *
from PySide.QtGui import *
import creaturecast_nodegraph.widgets.graphics_item.node as nod
import creaturecast_handlers.handlers as hdr

class NodeGraphWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super(NodeGraphWidget, self).__init__(*args, **kwargs)
        self.layout = QHBoxLayout(self)
        self.view = NodegraphView(self)
        self.layout.addWidget(self.view)
        hdr.selection_handler.selection_changed.connect(self.add_nodes)


    def add_nodes(self, nodes):
        for node in nodes:
            graphics_item = nod.Node(node)
            self.view.scene().addItem(graphics_item)

    def set_selection_handler(self, handler):
        self.view.selection_handler = handler
        handler.selection_changed.connect(self.add_nodes)

class NodegraphView(QGraphicsView):
    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)

        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.node_graph_scene = NodegraphScene()
        self.setScene(self.node_graph_scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self.setFrameShape(QFrame.NoFrame)
        self.zoom_rate = 0.001
        self.selection_handler = None

    def wheelEvent(self, event):

        (xfo, inv) = self.transform().inverted()
        top_left = xfo.map(self.rect().topLeft())
        bottom_right = xfo.map(self.rect().bottomRight())
        center = (top_left + bottom_right) * 0.5
        zoom_factor = 1.0 + event.delta() * self.zoom_rate
        transform = self.transform()
        # Limit zoom to 3x
        if transform.m22() * zoom_factor >= 2.0:
            return

        self.scale(zoom_factor, zoom_factor)

        # Call udpate to redraw background
        self.update()


class NodegraphScene(QGraphicsScene):
    grid = 30

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, QRectF(-1000, -1000, 2000, 2000), parent)

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QColor(90, 90, 90))
        left = int(rect.left()) - int((rect.left()) % self.grid)
        top = int(rect.top()) - int((rect.top()) % self.grid)
        right = int(rect.right())
        bottom = int(rect.bottom())
        lines = []
        for x in range(left, right, self.grid):
            lines.append(QLine(x, top, x, bottom))
        for y in range(top, bottom, self.grid):
            lines.append(QLine(left, y, right, y))
        painter.setPen(QPen(QColor(100, 100, 100)))
        painter.drawLines(lines)

    def mouseDoubleClickEvent(self, event):

        QGraphicsScene.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            if len(self.selectedItems()) == 2:
                edge = Edge(self.selectedItems()[0], self.selectedItems()[1])
                self.addItem(edge)
        QGraphicsScene.mousePressEvent(self, event)


class Node(QGraphicsRectItem):
    def __init__(self, rect=QRectF(-75, -15, 150, 30), parent=None):
        QGraphicsRectItem.__init__(self, rect, parent)
        self.edges = []
        self.setZValue(1)
        self.setBrush(Qt.darkGray)
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges)

    def addEdge(self, edge):
        self.edges.append(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            self.setBrush(Qt.green if value else Qt.darkGray)

        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edges:
                edge.adjust()

        return QGraphicsItem.itemChange(self, change, value)


class Edge(QGraphicsLineItem):
    def __init__(self, source, dest, parent=None):
        QGraphicsLineItem.__init__(self, parent)
        self.source = source
        self.dest = dest
        self.source.addEdge(self)
        self.dest.addEdge(self)
        self.setPen(QPen(Qt.red, 1.75))
        self.adjust()

    def adjust(self):
        self.prepareGeometryChange()
        self.setLine(QLineF(self.dest.pos(), self.source.pos()))



