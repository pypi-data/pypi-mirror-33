#Typing imports
import typing as typ

#External imports
from PyQt5 import QtCore, QtGui, QtWidgets # type: ignore
import qdarkstyle                          # type: ignore
#Internal Imports
from catalog.gui.job_maker import JobMakerGUI
from catalog.gui.relauncher import  RelaunchGUI


class CataLogGUI(QtWidgets.QMainWindow):
    def __init__(self
                ,parent          : typ.Any       = None
                ,guis            : list          = []
                ,gui_names       : list          = ['Job Maker', "Relauncher"]
                ) -> None:
        QtWidgets.QWidget.__init__(self, parent)
        self.guis = guis
        self.gui_names = gui_names
        self.setupUi()

    def setupUi(self) -> None:
        """
        Create the UI for the CataLogGUI object
        """
        self.setObjectName("Query")
        self.resize(1900, 732)
        self.setWindowTitle( "Query GUI")

        #Set Fonts for Push Buttons and Titles
        self.header_font = QtGui.QFont()
        self.header_font.setFamily("Helvetica Neue")
        self.header_font.setPointSize(15)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setFont(self.header_font)
        self.centralwidget.setObjectName("centralwidget")
        self.central_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.central_layout.setObjectName("central_layout")
        self.central_tabWidget = QtWidgets.QTabWidget()
        self.central_layout.addWidget(self.central_tabWidget)

        self.tabs        = [] # type: list
        self.tab_layouts = [] # type: list
        for gui,name in zip(self.guis,self.gui_names):
            self.tabs.append(QtWidgets.QWidget())
            self.tab_layouts.append(QtWidgets.QHBoxLayout(self.tabs[len(self.tabs)-1]))
            self.tab_layouts[len(self.tabs)-1].addWidget(gui)
            self.central_tabWidget.addTab(self.tabs[len(self.tabs)-1],name)


        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1319, 22))
        self.menubar.setDefaultUp(True)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.central_tabWidget.setCurrentIndex(0)
        self.central_tabWidget.setDocumentMode(True)

def main() -> None:
    import sys,os
    os.environ['QT_API']='pyqt5'
    sys.argv.append('--disable-web-security')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment(is_pyqtgraph=False))
    query = """
SELECT job_id,
   job_name,
   USER,
   stordir
FROM job
JOIN relax_job USING (job_id)
JOIN calc USING (calc_id)
JOIN calc_other USING (calc_other_id)
JOIN finaltraj USING (job_id)
JOIN struct USING (struct_id)
LEFT JOIN surface USING (struct_id)
LEFT JOIN bulk USING (struct_id)
LEFT JOIN molecule USING (struct_id)
WHERE user = 'aayush' and cell_dofree != ''
LIMIT 100
    """
    guis = [JobMakerGUI(query=query),RelaunchGUI()]
    gui_names = ['Job Maker','Relauncher']
    gui = CataLogGUI(guis = guis, gui_names = gui_names)
    gui.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
