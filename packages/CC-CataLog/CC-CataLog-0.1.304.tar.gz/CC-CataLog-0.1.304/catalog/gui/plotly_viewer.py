#Typing imports
import typing as typ

#External imports
from PyQt5 import QtWebEngineWidgets, QtGui, QtWidgets, QtCore # type: ignore
import ase                                                     # type: ignore
from ase.visualize import view                                 # type: ignore
import os
#Internal Imports
from catalog.misc.plotly_atoms import PlotlyAtoms


plotly_json_path = os.path.join(os.path.dirname(__file__),'plotly-latest.min.js')
plotly_url       = QtCore.QUrl.fromLocalFile(plotly_json_path).toString()

class PlotlyView(QtWidgets.QWidget):
    def __init__(self
                ,list_of_atoms_obj : typ.List[ase.Atoms]
                ,parent            : typ.Any            = None
                )-> None:
        super(PlotlyView,self).__init__(parent)
        self.setupUi()
        self.list_of_atoms_obj = list_of_atoms_obj
        self.plotly_atoms      = [PlotlyAtoms(atoms_obj = atoms) for atoms in list_of_atoms_obj]
        self.plotly_htmls      = [plotly_atoms.plot(offline = True) for plotly_atoms in self.plotly_atoms]
        self.current_index     = 0
        self._build_html()
        self._connect_signals()

    def _connect_signals(self) -> None:
        self.previous_button.clicked.connect(self._previous)
        self.next_button.clicked.connect(self._next)
        self.view_button.clicked.connect(self._view_ase)

    def setupUi(self) -> None:
        self.layout          = QtWidgets.QVBoxLayout(self)
        self.viewer          = QtWebEngineWidgets.QWebEngineView()
        self.layout.addWidget(self.viewer)
        self.button_box      = QtWidgets.QGroupBox()
        self.button_layout   = QtWidgets.QHBoxLayout(self.button_box)
        self.previous_button = QtWidgets.QPushButton("Previous Atoms Object")
        self.view_button     = QtWidgets.QPushButton("View in ASE GUI")
        self.next_button     = QtWidgets.QPushButton("Next Atoms Object")
        self.button_layout.addWidget(self.previous_button)
        self.button_layout.addWidget(self.view_button)
        self.button_layout.addWidget(self.next_button)
        self.layout.addWidget(self.button_box)
        self.layout.setStretch(0,1)

    def _next(self) -> None:
        self.current_index += 1
        self.current_index = min(len(self.plotly_atoms)-1,self.current_index)
        self._build_html()

    def _view_ase(self) -> None:
        view(self.list_of_atoms_obj[self.current_index])

    def _previous(self) -> None:
        self.current_index -= 1
        self.current_index = max(0,self.current_index)
        self._build_html()


    def _build_html(self) -> None:
        raw_html    = '<html><head><meta charset ="utf-8" />'
        raw_html   += '<script src="{}"></script></head>'.format(plotly_url)
        raw_html   += '<body>'
        raw_html   += '<div align="center">'
        raw_html   += self.plotly_htmls[self.current_index]
        raw_html   += '</div>'
        raw_html   += '</body></html>'
        self.viewer.setHtml(raw_html)
        self.viewer.page()
        # self.viewer.update()
