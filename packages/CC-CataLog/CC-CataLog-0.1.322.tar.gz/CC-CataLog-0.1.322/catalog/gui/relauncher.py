#Typing imports
import typing as typ

#External imports
import qdarkstyle                                 # type: ignore
import sqlparse                                   # type: ignore
import time
from ase.visualize import view                    # type: ignore
from PyQt5 import QtCore, QtGui, QtWidgets, QtSql # type: ignore

#Internal Imports
import catalog.fw.incomplete as inc
from catalog.gui.launch_form import LaunchForm
from catalog.datalog.db_utils import Query
from catalog.misc.sql_utils import *
from catalog.misc.atoms import json_to_traj,new_view

user = os.environ['USER']

class RelaunchGUI(QtWidgets.QWidget):
    def __init__(self
                ,parent          : typ.Any       = None
                ,incomplete_cols : typ.List[str] = ['status','cluster','queue','Time','nodes','job_name','created_on','updated_on','_launch_dir']
                ) -> None:
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi()

        #Build the table
        self.incomplete_cols = incomplete_cols
        start = time.time()
        self.incomplete_rows = self.load_incomplete_jobs()
        if len(self.incomplete_rows) == 0:
            self.set_message('No Incomplete Jobs!\nGet Submitting You Slacker!')
        end = time.time()

        self._build_table()
        self.regex_combobox.addItems(['fwid']+self.incomplete_cols)
        self._connect_signals()

    def _connect_signals(self) -> None:
        #Connect table clicking
        self.table.clicked.connect(self._table_click)

        #Connect push buttons
        self.push_update.clicked.connect(self._update)
        self.push_quit.clicked.connect(self._quit)
        self.push_view.clicked.connect(self._view)
        self.push_relaunch.clicked.connect(self._relaunch)

        #Connect RegEx Functions
        self.regex_edit.textChanged.connect(self.on_lineEdit_textChanged)
        self.regex_combobox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)
        self.horizontalHeader = self.table.horizontalHeader()
        self.horizontalHeader.sectionClicked.connect(self.on_view_horizontalHeader_sectionClicked)

    def keyPressEvent(self, event : typ.Any)->None:
        k = event.key()
        m = int(event.modifiers())
        if QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+W'):
            self._quit(event)
        elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+C'):
            self._copy()

    def _build_table(self, reload_incomplete_rows : bool = False)->None:
        self.table.setWordWrap(True)
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['fwid']+self.incomplete_cols)
        self.update_table_contents(reload_incomplete_rows = reload_incomplete_rows)
        self.proxy = QtCore.QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.table.setModel(self.proxy)
        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0,QtCore.Qt.DescendingOrder)

        #Remove editing capabilities and set only row selection
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def update_table_contents(self
                             ,reload_incomplete_rows : bool = True
                             ) -> None:
        inc.detect()
        if reload_incomplete_rows:
            self.incomplete_rows = self.load_incomplete_jobs()
        #Name the Rows
        for i_row, row_data in enumerate(self.incomplete_rows):
            #Set last column to be a check box
            self.model.invisibleRootItem().appendRow(
            [QtGui.QStandardItem(str(row_val)) for row_val in row_data])

    def load_incomplete_jobs(self)->list:
        current_incomplete_jobs = inc.table_data(self.incomplete_cols)
        if current_incomplete_jobs is None:
            current_incomplete_jobs = []
        return current_incomplete_jobs

    def _table_click(self,event : typ.Any)->None:
        model_index = self.table.model().mapToSource(event)
        self.clicked_model_index = model_index


    def _copy(self)->None:
        sys_clip = QtWidgets.QApplication.clipboard()
        current_cell_selected = self.model.item(self.clicked_model_index.row(),self.clicked_model_index.column()).text()
        sys_clip.setText(current_cell_selected)

    def _update(self,event : typ.Any)->None:
        self.set_message('Updating Table...')
        self.model.clear()
        self._build_table(reload_incomplete_rows = True)
        self.set_message('Table Updated')

    def _view(self,event : typ.Any)->None:
        fwids_to_view     = self.get_selected_fw_ids()
        if len(fwids_to_view)>0:
            fw_dicts          = map(inc.lpad.get_fw_dict_by_id,fwids_to_view)
            atoms_to_view     = [json_to_traj(fwdict['spec']['params']['inittraj']) for fwdict in fw_dicts]
            new_view(atoms_to_view)

    def _quit(self,
              event : typ.Any) -> None:
        """
        Halts the program
        """
        reply = self.check_with_user()
        if reply:
            self.close()
            QtWidgets.QApplication.exit()

    def _relaunch(self,
               event : typ.Any) -> None:
        """
        Halts the program
        """
        fwids_to_relaunch = self.get_selected_fw_ids()
        if self.central_tabWidget.count() == 1:
            if len(fwids_to_relaunch)>0:
                form = self.central_tabWidget.addTab(LaunchForm(fwids_to_relaunch,self),"Launch Form")
                self.central_tabWidget.setCurrentIndex(1)
            else:
                self.set_message('Please select a job to relaunch')
        else:
            self.set_message('Please close the existing Form to launch new jobs')

    def get_selected_fw_ids(self)->typ.List[int]:
        indexes          = self.table.selectedIndexes()
        if len(indexes)>0:
            selected_job_ids = set()                                                # type: ignore
            for index in sorted(indexes):
                model_index = self.table.model().mapToSource(index)
                selected_job_ids.update([int(self.model.item(model_index.row(),0).text())])
            selected_job_ids = list(selected_job_ids)                               # type: ignore
        else:
            selected_job_ids = []
        return selected_job_ids


    @staticmethod
    def check_with_user(message : str = 'Are you sure you want to quit?') -> bool:
        reply = QtWidgets.QMessageBox.question(None, 'Message',
                     message, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    def set_message(self
                   ,text  : str  = ''
                   ,clear : bool = False
                   ) -> None:
        if clear:
            self.message_box.clear()
        self.message_box.appendPlainText(text)

    def setupUi(self) -> None:
        """
        Create the UI for the QueryGUI object
        """
        self.setObjectName("Query")
        self.resize(1900, 732)
        self.setWindowTitle( "Query GUI")

        #Set Fonts for Push Buttons and Titles
        self.header_font = QtGui.QFont()
        self.header_font.setFamily("Helvetica Neue")
        self.header_font.setPointSize(15)

        # self.centralwidget = QtWidgets.QWidget(self)
        # self.centralwidget.setFont(self.header_font)
        # self.centralwidget.setObjectName("centralwidget")
        self.central_layout = QtWidgets.QHBoxLayout(self)
        self.central_layout.setObjectName("central_layout")
        self.central_tabWidget = QtWidgets.QTabWidget()
        self.central_tabWidget.tabBar().hide()
        self.central_layout.addWidget(self.central_tabWidget)

        self.incomplete_jobs_tab        = QtWidgets.QWidget()
        self.incomplete_jobs_tab_layout = QtWidgets.QHBoxLayout(self.incomplete_jobs_tab)

        ##################
        #Create Left Frame and set its layout
        ##################
        self.left_frame = QtWidgets.QFrame()
        self.left_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.left_frame.setFrameShape(QtWidgets.QFrame.Panel)
        # self.left_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        # self.left_frame.setLineWidth(2)
        # self.left_frame.setMidLineWidth(1)
        self.left_frame_layout = QtWidgets.QVBoxLayout(self.left_frame)

        #Create push button box and fill it with push buttons
        ##################
        self.push_group = QtWidgets.QGroupBox(self.left_frame)
        self.push_group.setFont(self.header_font)

        self.push_group.setObjectName("push_group")
        self.push_group_layout = QtWidgets.QVBoxLayout(self.push_group)
        self.push_group_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.push_group_layout.setObjectName("push_group_layout")

        #Create push_update button
        ##################
        self.push_update = QtWidgets.QPushButton(self.push_group)
        self.push_update.setFont(self.header_font)
        self.push_update.setObjectName("push_update")
        self.push_update.setText( "Update Table")
        self.push_group_layout.addWidget(self.push_update)

        #Create push_lanch button
        ##################
        self.push_relaunch = QtWidgets.QPushButton(self.push_group)
        self.push_relaunch.setFont(self.header_font)
        self.push_relaunch.setObjectName("push_relaunch")
        self.push_relaunch.setText( "Manage Selected Jobs")
        self.push_group_layout.addWidget(self.push_relaunch)


        # #Create push_check_select button
        # ##################
        # self.push_check_select = QtWidgets.QPushButton(self.push_group)
        # self.push_check_select.setFont(self.header_font)
        # self.push_check_select.setObjectName("push_check_select")
        # self.push_check_select.setText( "Check Selection")
        # self.push_group_layout.addWidget(self.push_check_select)
        #
        #Create view button
        ##################
        self.push_view = QtWidgets.QPushButton(self.push_group)
        self.push_view.setFont(self.header_font)
        self.push_view.setObjectName("push_view")
        self.push_view.setText( "View Selection")
        self.push_group_layout.addWidget(self.push_view)

        #Create push_quit button
        ##################
        self.push_quit = QtWidgets.QPushButton(self.push_group)
        self.push_quit.setFont(self.header_font)
        self.push_quit.setObjectName("push_quit")
        self.push_quit.setText( "Quit")
        self.push_group_layout.addWidget(self.push_quit)

        self.left_frame_layout.addWidget(self.push_group)

        #Create RegEx box
        ##################
        self.regex_group = QtWidgets.QGroupBox(self.left_frame)
        self.regex_group.setFont(self.header_font)
        self.regex_group.setTitle("RegEx Filters")
        self.regex_group_layout = QtWidgets.QFormLayout(self.regex_group)
        self.regex_group_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.regex_group_layout.setObjectName("regex_group_layout")

        #Create RegEx combobox and editor
        ##################
        self.regex_combobox = QtWidgets.QComboBox()
        self.regex_group_layout.addRow(QtWidgets.QLabel("Column:"), self.regex_combobox)
        self.regex_edit     = QtWidgets.QLineEdit()
        self.regex_group_layout.addRow(QtWidgets.QLabel("Regex String:"),self.regex_edit)
        self.left_frame_layout.addWidget(self.regex_group)

        #Create message box
        ##################
        self.group_message = QtWidgets.QGroupBox(self.left_frame)
        self.group_message.setFont(self.header_font)
        self.group_message.setObjectName("group_message")
        self.group_message.setTitle( "Messages")
        self.group_message_layout = QtWidgets.QVBoxLayout(self.group_message)
        self.group_message_layout.setObjectName("group_message_layout")
        self.message_box = QtWidgets.QPlainTextEdit(self.group_message)
        self.message_box.setReadOnly(True)
        self.message_box.setObjectName("message_box")
        self.group_message.setTitle( "Messages")

        #Add the message and push_button box to the left_frame
        ##################
        self.group_message_layout.addWidget(self.message_box)
        self.left_frame_layout.addWidget(self.group_message)
        self.incomplete_jobs_tab_layout.addWidget(self.left_frame)

        #Create Right Frame and set its layout
        ##################
        self.right_frame = QtWidgets.QFrame()
        self.right_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.right_frame.setFrameShape(QtWidgets.QFrame.Panel)
        # self.right_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        # self.right_frame.setLineWidth(2)
        # self.right_frame.setMidLineWidth(0)
        # self.right_frame.setObjectName("right_frame")
        self.right_frame_layout = QtWidgets.QVBoxLayout(self.right_frame)
        self.right_frame_layout.setObjectName("right_frame_layout")

        #Create Result Box
        ##################
        self.group_results = QtWidgets.QGroupBox(self.right_frame)
        self.group_results.setFont(self.header_font)
        self.group_results.setAcceptDrops(False)
        self.group_results.setObjectName("group_results")
        self.group_results.setTitle( "Incomplete Jobs")
        self.group_results_layout = QtWidgets.QVBoxLayout(self.group_results)
        # self.group_results_layout.setContentsMargins(5, 5, 5, 5)
        self.group_results_layout.setObjectName("group_results_layout")
        self.group_results.setTitle( "Incomplete Jobs")
        self.table = QtWidgets.QTableView(self.group_results)
        self.table.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.table.setFrameShadow(QtWidgets.QFrame.Raised)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSortingEnabled(False)
        self.table.setObjectName("table")
        self.group_results_layout.addWidget(self.table)
        self.right_frame_layout.addWidget(self.group_results)
        self.incomplete_jobs_tab_layout.addWidget(self.right_frame)
        # self.right_frame_layout.setStretch(1,1)
        self.incomplete_jobs_tab_layout.setStretch(1,1)

        self.central_tabWidget.addTab(self.incomplete_jobs_tab,"Query GUI")
        # self.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(self)



    def create_scroll_area(self, n_constraints : int = 3) -> None:
        """
        Creates the scroll area for the SQL form
        Mainly used for the add and remove constraints buttons

        Parameters
        ----------
        n_constraints : int
            number of constraints visible in the ui of the where clause
        """
        #Place the form in the contents of the scroll area
        self.scroll_contents = QtWidgets.QWidget()
        self.scroll_contents.setGeometry(QtCore.QRect(0, 0, 525, 330))
        self.scroll_contents.setObjectName("scroll_contents")
        self.scroll_contents_layout = QtWidgets.QFormLayout(self.scroll_contents)
        self.scroll_contents_layout.setLabelAlignment(QtCore.Qt.AlignCenter)
        self.scroll_contents_layout.setObjectName("scroll_contents_layout")

        #Create Select label
        self.label_select = QtWidgets.QLabel(self.scroll_contents)
        self.label_select.setFont(self.header_font)
        self.label_select.setAlignment(QtCore.Qt.AlignCenter)
        self.label_select.setObjectName("label_select")
        self.label_select.setText( "SELECT")
        self.scroll_contents_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_select)

        #Create Select edit box
        self.select_edit = QtWidgets.QLineEdit(self.scroll_contents)
        self.select_edit.setObjectName("select_edit")
        self.select_edit.setText( "*")
        self.scroll_contents_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.select_edit)

        #Create Where label
        self.label_where = QtWidgets.QLabel(self.scroll_contents)
        self.label_where.setFont(self.header_font)
        self.label_where.setAlignment(QtCore.Qt.AlignCenter)
        self.label_where.setObjectName("label_where")
        self.label_where.setText( "WHERE")
        self.scroll_contents_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_where)

        #Create Constraint fields
        self.n_constraints = 0
        self.constraint_columns    = [] # type: ignore
        self.constraint_conditions = [] # type: ignore
        self.constraint_edits      = [] # type: ignore
        self.layout_constraints    = [] # type: ignore

        default_columns = ['job_id','user','system_type']+['']*(n_constraints-3)
        [self.create_constraint(col) for col in default_columns] # type: ignore

        #Create Group By label
        self.label_group_by = QtWidgets.QLabel(self.scroll_contents)
        self.label_group_by.setFont(self.header_font)
        self.label_group_by.setAlignment(QtCore.Qt.AlignCenter)
        self.label_group_by.setObjectName("label_group_by")
        self.label_group_by.setText( "GROUP BY")
        self.scroll_contents_layout.setWidget(self.scroll_contents_layout.count(), QtWidgets.QFormLayout.LabelRole, self.label_group_by)
        self.group_by_edit = QtWidgets.QLineEdit(self.scroll_contents)
        self.group_by_edit.setObjectName("group_by_edit")
        self.scroll_contents_layout.setWidget(self.scroll_contents_layout.count(), QtWidgets.QFormLayout.FieldRole, self.group_by_edit)

        #Create Limit label
        self.label_limit = QtWidgets.QLabel(self.scroll_contents)
        self.label_limit.setFont(self.header_font)
        self.label_limit.setAlignment(QtCore.Qt.AlignCenter)
        self.label_limit.setObjectName("label_limit")
        self.label_limit.setText( "LIMIT")
        self.scroll_contents_layout.setWidget(self.scroll_contents_layout.count(), QtWidgets.QFormLayout.LabelRole, self.label_limit)
        self.limit_edit = QtWidgets.QLineEdit(self.scroll_contents)
        self.limit_edit.setObjectName("limit_edit")
        self.scroll_contents_layout.setWidget(self.scroll_contents_layout.count(), QtWidgets.QFormLayout.FieldRole, self.limit_edit)
        self.scroll_form.setWidget(self.scroll_contents)

    def create_constraint(self, column_name : str = '') -> None:
        """
        A UI function for making each row for a constraint in the SQL Form.

        Parameters
        ----------
        column_name : str
            name of column to be set in the line edit box of the constraint row
        """
        #Create Column Editor
        self.constraint_columns.append(QtWidgets.QLineEdit(self.scroll_contents))
        self.constraint_columns[self.n_constraints].setAlignment(QtCore.Qt.AlignCenter)
        self.constraint_columns[self.n_constraints].setText(column_name)
        self.constraint_columns[self.n_constraints].setObjectName("constraint_column[self.n_constraints]")
        self.scroll_contents_layout.setWidget(self.n_constraints+3, QtWidgets.QFormLayout.LabelRole, self.constraint_columns[self.n_constraints])

        self.layout_constraints.append(QtWidgets.QHBoxLayout())
        self.layout_constraints[self.n_constraints].setObjectName("layout_constraint_1")

        #Create Condition combo box
        self.constraint_conditions.append(QtWidgets.QComboBox(self.scroll_contents))
        self.constraint_conditions[self.n_constraints].setObjectName("constraint_conditions_{}".format(self.n_constraints))
        combo_box_strings = ["Equal","Not Equal","Like","Not Like","In"]
        [self.constraint_conditions[self.n_constraints].addItem(item) for item in combo_box_strings]
        self.layout_constraints[self.n_constraints].addWidget(self.constraint_conditions[self.n_constraints])

        #Create Constraint Editor
        self.constraint_edits.append(QtWidgets.QLineEdit(self.scroll_contents))
        self.constraint_edits[self.n_constraints].setObjectName("constraint_edits[self.n_constraints]")
        self.layout_constraints[self.n_constraints].addWidget(self.constraint_edits[self.n_constraints])
        self.scroll_contents_layout.setLayout(self.n_constraints+3, QtWidgets.QFormLayout.FieldRole, self.layout_constraints[self.n_constraints])
        self.n_constraints += 1

    @QtCore.pyqtSlot(int)                                            # type: ignore
    def on_view_horizontalHeader_sectionClicked(self, logicalIndex): # type: ignore
        self.logicalIndex   = logicalIndex
        self.menuValues     = QtWidgets.QMenu(self)
        self.signalMapper   = QtCore.QSignalMapper(self)

        self.regex_combobox.blockSignals(True)
        self.regex_combobox.setCurrentIndex(self.logicalIndex)
        self.regex_combobox.blockSignals(False)

        valuesUnique = [    self.model.item(row, self.logicalIndex).text()
                            for row in range(self.model.rowCount())
                            ]
        if len(set(valuesUnique)) == len(self.incomplete_rows):
            return
        actionAll = QtWidgets.QAction("All", self)
        actionAll.triggered.connect(self.on_actionAll_triggered)
        self.menuValues.addAction(actionAll)
        self.menuValues.addSeparator()

        for actionNumber, actionName in enumerate(sorted(list(set(valuesUnique)))):
            action = QtWidgets.QAction(actionName, self)
            self.signalMapper.setMapping(action, actionNumber)
            action.triggered.connect(self.signalMapper.map)
            self.menuValues.addAction(action)

        self.signalMapper.mapped.connect(self.on_signalMapper_mapped)

        headerPos = self.table.mapToGlobal(self.horizontalHeader.pos())

        posY = headerPos.y() + self.horizontalHeader.height()
        posX = headerPos.x() + self.horizontalHeader.sectionPosition(self.logicalIndex)

        self.menuValues.exec_(QtCore.QPoint(posX, posY))

    @QtCore.pyqtSlot()                                         # type: ignore
    def on_actionAll_triggered(self)->None:                    # type: ignore
        filterColumn = self.logicalIndex
        filterString = QtCore.QRegExp( "",
                                        QtCore.Qt.CaseInsensitive,
                                        QtCore.QRegExp.RegExp
                                        )
        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    @QtCore.pyqtSlot(int)                                      # type: ignore
    def on_signalMapper_mapped(self, i : typ.Any)->None:       # type: ignore
        stringAction = self.signalMapper.mapping(i).text()
        filterColumn = self.logicalIndex
        filterString = QtCore.QRegExp( stringAction,
                                        QtCore.Qt.CaseSensitive,
                                        QtCore.QRegExp.FixedString
                                        )
        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    @QtCore.pyqtSlot(str)                                      # type: ignore
    def on_lineEdit_textChanged(self, text : typ.Any) -> None: # type: ignore
        search = QtCore.QRegExp( text,
                                    QtCore.Qt.CaseInsensitive,
                                    QtCore.QRegExp.RegExp
                                    )

        self.proxy.setFilterRegExp(search)

    @QtCore.pyqtSlot(int)
    def on_comboBox_currentIndexChanged(self, index):          # type: ignore
        self.proxy.setFilterKeyColumn(index)




if __name__ == "__main__":
    import sys,os
    os.environ['QT_API']='pyqt5'
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment(is_pyqtgraph=False))

    gui = RelaunchGUI()
    gui.showMaximized()
    sys.exit(app.exec_())
