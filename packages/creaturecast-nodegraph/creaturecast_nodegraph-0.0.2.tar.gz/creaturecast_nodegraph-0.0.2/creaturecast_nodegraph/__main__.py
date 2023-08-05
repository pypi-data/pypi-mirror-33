import sys
import widgets.node_graph_widget as ngw
from qtpy.QtWidgets import QApplication
import creaturecast_nodegraph.services.get_stylesheet as stl

app = QApplication(sys.argv)
app.setStyleSheet(stl.get_stylesheet('slate'))
mainWin = ngw.NodeGraphWidget()
mainWin.show()
sys.exit(app.exec_())