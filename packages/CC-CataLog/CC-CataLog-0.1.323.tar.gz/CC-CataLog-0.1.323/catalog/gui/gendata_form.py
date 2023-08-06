#Typing imports
import typing as typ

#External imports
from PyQt5 import QtCore, QtGui, QtWidgets # type: ignore
import qdarkstyle                          # type: ignore
import logging, inspect


#Internal Imports
import catalog.gendata.gendata as gendata
from catalog.datalog.db_utils import Query
from catalog.misc.sql_utils import *
from catalog.gui.plotly_viewer import PlotlyView
from catalog.jobs.cluster import cluster_dict
from adsorber import filter_functions as ff


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent : typ.Any) -> None:
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record : typ.Any)-> None:
        msg = self.format(record)
        self.widget.appendPlainText(msg)

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtWidgets.QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

class GenDataForm(QtWidgets.QMainWindow):
    def __init__(self
                ,job_type : str
                ,job_ids   : typ.List[int]
                ,parent    : typ.Any      = None
                )->None:
        super(GenDataForm, self).__init__()
        self.neglected_args    = ['limit','constraints','check_func','verbose'] #Args that user can specify

        self.gendata_functions = {'Adsorb'          : gendata.adsorb
                                 ,'Bare'            : gendata.bare
                                 ,'Bare All Facets' : gendata.bare_all_facets
                                 ,'Vacancy'         : gendata.vacancy}

        self.parent     = parent
        self.job_ids    = job_ids
        self.job_type   = job_type
        self.atoms_objs = Query(constraints = [JOB_IN_(job_ids)]).make_atoms()  # type: ignore
        self.arg_dict   = self.get_arg_dict(self.gendata_functions[self.job_type])

        self.setupUi()
        self._connect_signals()
        # self._update_input_table()
        logging.info('Hello')

    def _connect_signals(self)->None:
        self.push_submit.clicked.connect(self._submit)

    def _submit(self)-> None:
        print(self.job_ids)
        constraints       = [JOB_IN_(self.job_ids)]
        limit             = len(self.job_ids)
        gendata_kwargs    = self._get_gendata_kwargs_from_table()
        gendata_kwargs.update({'constraints': constraints
                              ,'limit'      : limit
                              ,'verbose'    : True
                              ,'check_func' : lambda x: True})
        gendata_obj       = self.gendata_functions[self.job_type](**gendata_kwargs)
        submit_kwargs     = self._get_cluster_info()
        gendata_dict      = gendata_obj.submit(**submit_kwargs)
        self.parent.central_tabWidget.removeTab(1)
        self.parent.central_tabWidget.setCurrentIndex(0)
        self.submited_ids = list(gendata_dict.values())


    def _get_gendata_kwargs_from_table(self) -> dict:
        kwargs = {} # type: ignore
        for row_i,arg_name in enumerate(self.arg_dict.keys()):
            try:
                if self.arg_edits[row_i].text() in [None,'']:
                    kwargs[arg_name] = None
                else:
                    kwargs[arg_name] = eval(self.arg_edits[row_i].text())
            except NameError:
                logging.error('Arguement {} has invalid value {}'.format(arg_name,self.arg_edits[row_i].text()))
                break
        return kwargs

    def _get_cluster_info(self) -> dict:
        walltime    = self.walltime_spinbox.value()
        clust_str   = self.cluster_combobox.currentText()
        nodes       = int(self.nodes_spinbox.value())
        return {'clust_str':clust_str,'nodes':nodes,'walltime':walltime}

    def get_arg_dict(self, func : typ.Any) -> dict:
        """
        returns a dictionary of arg_name:default_values for the input function
        """
        argspec          = inspect.getfullargspec(func)
        func_args        = argspec.args
        func_defaults    = argspec.defaults
        if func_args == []:
            return {}
        default_dict = dict(zip(func_args[-len(func_defaults):], func_defaults))
        return {arg : default_dict.get(arg) for arg in func_args if not arg in self.neglected_args}

    def setupUi(self) -> None:
        #Build Central Widget and set its layout
        self.centralwidget  = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        #Build top frame
        self.top_frame = QtWidgets.QFrame()
        self.top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.top_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.top_frame.setObjectName("frame")
        self.top_frame_layout = QtWidgets.QHBoxLayout(self.top_frame)
        self.top_frame_layout.setObjectName("top_frame_layout")

        #Build Push Box
        ###################
        self.push_box = QtWidgets.QGroupBox(self.top_frame)
        self.push_box.setObjectName("push_box")
        self.push_box_layout = QtWidgets.QFormLayout(self.push_box)
        self.push_box_layout.setObjectName("push_box_layout")

        #Create push_submit button
        self.push_submit = QtWidgets.QPushButton(self.push_box)
        self.push_submit.setObjectName("push_submit")
        self.push_submit.setText("Submit")
        self.push_box_layout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.push_submit)

        #Create Gendata label and comboBox
        self.gendata_label = QtWidgets.QLabel(self.push_box)
        self.gendata_label.setObjectName("gendata_label")
        self.gendata_label.setText("GenData Function")
        self.push_box_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.gendata_label)

        self.gendata_label = QtWidgets.QLabel(self.job_type)

        self.push_box_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.gendata_label)
        self.top_frame_layout.addWidget(self.push_box)

        #Create Cluster box
        self.cluster_box = QtWidgets.QGroupBox(self.top_frame)
        self.cluster_box.setObjectName("cluster_box")
        self.cluster_box.setTitle("Cluster Information")
        self.formLayout = QtWidgets.QFormLayout(self.cluster_box)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.formLayout.setObjectName("formLayout")

        #Walltime label and field
        self.walltime_label = QtWidgets.QLabel(self.cluster_box)
        self.walltime_label.setObjectName("walltime_label")
        self.walltime_label.setText("Walltime")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.walltime_label)
        self.walltime_spinbox = QtWidgets.QSpinBox(self.cluster_box)
        self.walltime_spinbox.setMinimum(1)
        self.walltime_spinbox.setMaximum(150)
        self.walltime_spinbox.setValue(40)
        self.walltime_spinbox.setObjectName("walltime_spinbox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.walltime_spinbox)

        #Cluster label and Field
        self.cluster_label = QtWidgets.QLabel(self.cluster_box)
        self.cluster_label.setObjectName("cluster_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.cluster_label)
        self.cluster_combobox = QtWidgets.QComboBox(self.cluster_box)
        self.cluster_combobox.setObjectName("cluster_combobox")
        self.cluster_combobox.addItems(list(cluster_dict.keys()))

        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.cluster_combobox)

        #Nodes label and Field
        self.nodes_label = QtWidgets.QLabel(self.cluster_box)
        self.nodes_label.setObjectName("nodes_label")
        self.nodes_label.setText("Nodes")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.nodes_label)
        self.nodes_spinbox = QtWidgets.QSpinBox(self.cluster_box)
        self.nodes_spinbox.setObjectName("nodes_spinbox")
        self.nodes_spinbox.setMinimum(1)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.nodes_spinbox)
        self.top_frame_layout.addWidget(self.cluster_box)

        #Create Message Box
        self.message_box = QtWidgets.QGroupBox(self.top_frame)
        self.message_box.setObjectName("message_box")
        self.message_box.setTitle("Messages")
        self.message_box_layout = QtWidgets.QHBoxLayout(self.message_box)
        self.message_box_layout.setObjectName("message_box_layout")

        #Setup logger
        self.logTextBox = QPlainTextEditLogger(self)
        # # You can format what is printed to text box
        self.logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().handlers = []
        logging.getLogger().addHandler(self.logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)
        self.message_box_layout.addWidget(self.logTextBox.widget)
        self.top_frame_layout.addWidget(self.message_box)
        self.verticalLayout.addWidget(self.top_frame)

        #Create bottom box and table
        self.bottom_box = QtWidgets.QGroupBox(self)
        self.bottom_box.setObjectName("bottom_box")
        self.bottom_box.setTitle("Inputs")
        self.bottom_box_layout = QtWidgets.QHBoxLayout(self.bottom_box)
        self.bottom_box_layout.setObjectName("bottom_box_layout")

        self.arg_box = QtWidgets.QGroupBox(self.bottom_box)
        self.arg_box.setTitle("Input Arguments")
        self.arg_box_layout = QtWidgets.QFormLayout(self.arg_box)

        self.arg_edits = []
        for arg, default in self.arg_dict.items():
            if isinstance(default,str):
                default = '\''+default+'\''
            self.arg_edits.append(QtWidgets.QLineEdit(str(default)))
            self.arg_box_layout.addRow(QtWidgets.QLabel(arg), self.arg_edits[-1])
        self.bottom_box_layout.addWidget(self.arg_box)

        self.plotly_viewer = PlotlyView(self.atoms_objs)
        self.bottom_box_layout.addWidget(self.plotly_viewer)
        self.bottom_box_layout.setStretch(1,1)

        self.verticalLayout.addWidget(self.bottom_box)

        self.verticalLayout.setStretch(1,1)
        self.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(self)




if __name__ == "__main__":
    import sys,os
    os.environ['QT_API']='pyqt5'
    sys.argv.append('--disable-web-security')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment(is_pyqtgraph=False))

    gui = GenDataForm(job_type = 'Adsorb',job_ids = [27457,27459])
    gui.showMaximized()
    sys.exit(app.exec_())
