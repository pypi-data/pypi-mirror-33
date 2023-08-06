#Typing imports
import typing as typ

#External imports
import qdarkstyle                                 # type: ignore
import sqlparse                                   # type: ignore
import time
from PyQt5 import QtCore, QtGui, QtWidgets, QtSql # type: ignore
#Internal Imports
from catalog.datalog.db_utils import Query, realDB
from catalog.misc.sql_utils import *
from catalog.misc.atoms import new_view
from catalog.gui.gendata_form import GenDataForm
from catalog.gui.launch_form import LaunchForm

user = os.environ['USER']


class JobMakerGUI(QtWidgets.QWidget):
    def __init__(self
                ,query       : str         = """SELECT job_id,
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
                                                WHERE 1
                                                LIMIT 100"""
                ,connectinfo : ConnectInfo = realDB
                ,parent      : typ.Any     = None
                ) -> None:
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi()


        #Build the table
        self.connectinfo = connectinfo
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
        db.setDatabaseName(self.connectinfo.db)
        db.setHostName(self.connectinfo.host)
        db.setUserName(self.connectinfo.user)
        db.setPassword(self.connectinfo.passwd)
        db.open()

        self.model = QtSql.QSqlQueryModel()
        start = time.time()
        self.expert_editor.appendPlainText(query)
        self.limit = 100
        self._update_query()
        self._beautify()
        self._build_table()
        self._connect_signals()

    def _connect_signals(self) -> None:
        self.push_add_constraint.clicked.connect(lambda x: self.create_scroll_area(self.n_constraints+1))
        self.push_remove_constraint.clicked.connect(lambda x: self.create_scroll_area(max([3,self.n_constraints-1])))
        self.table.clicked.connect(self._table_click)
        self.push_quit.clicked.connect(self._quit)
        self.push_view.clicked.connect(self._view)
        self.push_launch.clicked.connect(self._launch)
        self.push_query_expert.clicked.connect(self._update_query)
        self.push_query.clicked.connect(self._update_query)

        self.regex_edit.textChanged.connect(self.on_lineEdit_textChanged)
        self.regex_combobox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)
        self.horizontalHeader = self.table.horizontalHeader()
        self.horizontalHeader.sectionClicked.connect(self.on_view_horizontalHeader_sectionClicked)

    def keyPressEvent(self, event : typ.Any)->None:
        k = event.key()
        m = int(event.modifiers())
        if QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+Return'):
            self._update_query()
        elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+B'):
            self._beautify()
        elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+W'):
            self._quit(event)
        elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+C'):
            self._copy()

    def _build_table(self)->None:
        self.table.setWordWrap(True)
        self.proxy = QtCore.QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        #Remove editing capabilities and set only row selection
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def _table_click(self,event : typ.Any)->None:
        model_index = self.table.model().mapToSource(event)
        self.clicked_model_index = model_index

    def _beautify(self)->None:
        command        = self.expert_editor.toPlainText()
        self.expert_editor.clear()
        self.expert_editor.appendPlainText(sqlparse.format(command, reindent=True, keyword_case='upper'))

    def _update_query(self)->None:
        command = self._get_sqlcommand()
        if not 'limit' in command:
            command += ' limit {}'.format(self.limit)
        start = time.time()
        self.model.setQuery(command)
        fetchtime = round(time.time()-start,3)
        #Print to Message box
        if self.model.lastError().isValid():
            self.set_message('Query Failed\n'.format(self.model.rowCount()),clear = True)
            self.set_message(sqlparse.format(command, reindent=True, keyword_case='upper'))
            self.set_message(self.model.lastError().text())
        else:
            self.set_message('Query Executed Succesfully\n{} Rows Returned\n{} second\n'.format(self.model.rowCount(),fetchtime),clear = True)
            self.set_message(sqlparse.format(command, reindent=True, keyword_case='upper'))

        #Set the regex filter box
        self.regex_combobox.clear()
        if self.model.rowCount()>0:
            self.regex_combobox.addItems([self.model.record(0).fieldName(x) for x in range(self.model.record(0).count())])

    def _get_sqlcommand(self) -> str:
        if self.tabWidget.currentIndex() == 0:
            return self.expert_editor.toPlainText().lower()
        else:
            select_cmd = self.select_edit.text().lower()
            where_cmd = ''
            for n_con in range(self.n_constraints):
                col_name  = self.constraint_columns[n_con].text().replace(' ','')
                condition = self.constraint_conditions[n_con].currentText()
                if condition   == 'Equal':
                    condition = '='
                elif condition == 'Not Equal':
                    condition = '!='
                val       = self.constraint_edits[n_con].text().replace(' ','').replace('\'','')
                if all(map(lambda x: not x == '',[col_name,condition,val])):
                    if not where_cmd == '':
                        where_cmd += ' AND '
                    if '(' in val or '[' in val:
                        where_cmd  += " {} {} {} ".format(col_name,condition,val)
                    else:
                        where_cmd  += " {} {} '{}' ".format(col_name,condition,val)
            group_by_cmd = self.group_by_edit.text().replace(' ','')
            if where_cmd:
                where_cmd = ' WHERE '+where_cmd
            if group_by_cmd:
                group_by_cmd = ' GROUP BY '+group_by_cmd
            limit_cmd = self.limit_edit.text().lower()
            if limit_cmd:
                limit_cmd = ' LIMIT '+limit_cmd
            cmd = """
            SELECT {}
            FROM job
            JOIN relax_job USING (job_id)
            JOIN calc USING (calc_id)
            JOIN calc_other USING (calc_other_id)
            JOIN finaltraj USING (job_id)
            JOIN struct USING (struct_id)
            LEFT JOIN surface USING (struct_id)
            LEFT JOIN bulk USING (struct_id)
            LEFT JOIN molecule USING (struct_id)
            {}
            {}
            {}
             """.format(select_cmd,where_cmd,group_by_cmd,limit_cmd)
            return cmd
    def _copy(self)->None:
        sys_clip = QtWidgets.QApplication.clipboard()
        current_cell_selected = str(self.model.record(self.clicked_model_index.row()).value(self.clicked_model_index.column()))
        sys_clip.setText(current_cell_selected)

    def _get_selected_job_ids(self)->list:
        indexes          = self.table.selectedIndexes()
        if len(indexes)>0:
            selected_job_ids = set()                                                # type: ignore
            for index in sorted(indexes):
                model_index = self.table.model().mapToSource(index)
                record      = self.model.record(model_index.row())
                if record.contains('job_id'):
                    selected_job_ids.update([self.model.record(model_index.row()).value('job_id')])
                else:
                    self.set_message('!!!!WARNING!!!!\nPlease include the column job_id in \nyour query to launch or view jobs\n',clear =True)
                    return []
            selected_job_ids = list(selected_job_ids)                               # type: ignore
        else:
            selected_job_ids = []
        return selected_job_ids

    def _view(self,event : typ.Any)->None:
        selected_job_ids = self._get_selected_job_ids()
        if len(selected_job_ids)>0:
            temp_query       = Query(constraints = [JOB_IN_(selected_job_ids)])     # type: ignore
            atoms            = temp_query.make_atoms()
            new_view(atoms)
        else:
            self.set_message("No Jobs selected\n")


    def _launch(self, event : typ.Any)-> None:
            """
            Halts the program
            """
            selected_job_ids = self._get_selected_job_ids()
            if self.central_tabWidget.count() == 1:
                if len(selected_job_ids)>0:
                    #Open up a dialog box to ask the user which file to view
                    dialogbox         = QtWidgets.QInputDialog()
                    job_types = ['Adsorb'
                                ,'Bare'
                                ,'Bare All Facets'
                                ,'Vacancy'         ]
                    job_type, ok = dialogbox.getItem(self, 'Job Type Selector','Select a job type to submit:',job_types,0,False)
                    #View that traj file
                    if job_type and ok:
                        form = self.central_tabWidget.addTab(GenDataForm(job_type = job_type, job_ids = selected_job_ids,parent = self),"Launch Form")
                        self.central_tabWidget.setCurrentIndex(1)
                else:
                    self.set_message('Please select a job to relaunch')
            else:
                self.set_message('Please close the existing Form to launch new jobs')

    def _quit(self,
              event : typ.Any) -> None:
        """
        Halts the program
        """
        reply = self.check_with_user()
        if reply:
            self.close()
            QtWidgets.QApplication.exit()

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

        self.query_tab        = QtWidgets.QWidget()
        self.query_tab_layout = QtWidgets.QHBoxLayout(self.query_tab)

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

        #Create push_view button
        ##################
        self.push_view = QtWidgets.QPushButton(self.push_group)
        self.push_view.setFont(self.header_font)
        self.push_view.setObjectName("push_view")
        self.push_view.setText( "View Selection")
        self.push_group_layout.addWidget(self.push_view)

        #Create push_lanch button
        ##################
        self.push_launch = QtWidgets.QPushButton(self.push_group)
        self.push_launch.setFont(self.header_font)
        self.push_launch.setObjectName("push_launch")
        self.push_launch.setText( "Launch Jobs From Selection")
        self.push_group_layout.addWidget(self.push_launch)

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
        self.query_tab_layout.addWidget(self.left_frame)

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
        self.group_results.setTitle( "Query Results")
        self.group_results_layout = QtWidgets.QVBoxLayout(self.group_results)
        # self.group_results_layout.setContentsMargins(5, 5, 5, 5)
        self.group_results_layout.setObjectName("group_results_layout")
        self.group_results.setTitle( "Query Results")
        self.table = QtWidgets.QTableView(self.group_results)
        self.table.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.table.setFrameShadow(QtWidgets.QFrame.Raised)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSortingEnabled(False)
        self.table.setObjectName("table")
        self.group_results_layout.addWidget(self.table)
        self.right_frame_layout.addWidget(self.group_results)

        # #Pretty Line
        # ##################
        # self.line = QtWidgets.QFrame(self.right_frame)
        # self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        # self.line.setLineWidth(3)
        # self.line.setMidLineWidth(1)
        # self.line.setFrameShape(QtWidgets.QFrame.HLine)
        # self.right_frame_layout.addWidget(self.line)

        ##################
        #Create Tab Widget
        ##################
        self.group_query = QtWidgets.QGroupBox(self.right_frame)
        self.group_query.setMaximumHeight(500)
        self.group_query.setFont(self.header_font)
        self.group_query.setFlat(True)
        self.group_query.setObjectName("group_query")
        self.group_query.setTitle( "Queries")
        self.group_query_layout = QtWidgets.QVBoxLayout(self.group_query)
        self.group_query_layout.setContentsMargins(12, 12, 12, 12)
        self.group_query_layout.setObjectName("group_query_layout")

        self.tabWidget = QtWidgets.QTabWidget(self.group_query)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")

        #Create Expert Tab
        ##################
        self.expert_tab = QtWidgets.QWidget()
        self.expert_tab.setObjectName("expert_tab")
        self.expert_tab_layout = QtWidgets.QVBoxLayout(self.expert_tab)
        self.expert_tab_layout.setObjectName("expert_tab_layout")
        #######Add Plain Text editor
        self.group_expert_editor = QtWidgets.QGroupBox(self.expert_tab)
        self.group_expert_editor.setFont(self.header_font)
        self.group_expert_editor.setObjectName("group_expert_editor")
        self.group_expert_editor.setTitle( "Direct SQL Statement (Cmd+Enter to query)")
        self.group_expert_editor_layout = QtWidgets.QHBoxLayout(self.group_expert_editor)
        self.group_expert_editor_layout.setObjectName("group_expert_editor_layout")
        self.expert_editor = QtWidgets.QPlainTextEdit(self.group_expert_editor)
        self.expert_editor.setObjectName("expert_editor")
        self.group_expert_editor_layout.addWidget(self.expert_editor)
        self.expert_tab_layout.addWidget(self.group_expert_editor)
        #######Add Query Push Button
        self.layout_push_expert = QtWidgets.QHBoxLayout()
        self.layout_push_expert.setObjectName("layout_push_expert")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_push_expert.addItem(spacerItem)
        self.push_query_expert = QtWidgets.QPushButton(self.expert_tab)
        self.push_query_expert.setObjectName("push_query_expert")
        self.push_query_expert.setText("Query (Ctrl/Cmd+Enter)")
        #######Place everything in the tab widget
        self.layout_push_expert.addWidget(self.push_query_expert)
        self.expert_tab_layout.addLayout(self.layout_push_expert)
        self.tabWidget.addTab(self.expert_tab, "SQL Expert")

        #Create Form Tab
        ##################
        self.form_tab = QtWidgets.QWidget()
        self.form_tab.setObjectName("form_tab")
        self.group_form_layout = QtWidgets.QGridLayout(self.form_tab)
        self.group_form_layout.setObjectName("group_form_layout")
        self.group_form = QtWidgets.QGroupBox(self.form_tab)
        self.group_form.setFont(self.header_font)
        self.group_form.setObjectName("group_form")
        self.group_form.setTitle( "Query Form")

        #Create a scroll area for the form
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.group_form)
        self.horizontalLayout_5.setContentsMargins(12, 12, 12, 12)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.scroll_form = QtWidgets.QScrollArea(self.group_form)
        self.scroll_form.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_form.setWidgetResizable(True)
        self.scroll_form.setObjectName("scroll_form")

        self.create_scroll_area(4)

        #Add to the widget layout and add query push button
        self.horizontalLayout_5.addWidget(self.scroll_form)
        self.group_form_layout.addWidget(self.group_form, 0, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.push_add_constraint = QtWidgets.QPushButton(self.form_tab)
        self.push_add_constraint.setObjectName("push_add_constraint")
        self.push_add_constraint.setText("Add Constraint")
        self.horizontalLayout.addWidget(self.push_add_constraint)
        self.push_remove_constraint = QtWidgets.QPushButton(self.form_tab)
        self.push_remove_constraint.setObjectName("push_remove_constraint")
        self.push_remove_constraint.setText("Remove Constraint")
        self.horizontalLayout.addWidget(self.push_remove_constraint)
        self.push_query = QtWidgets.QPushButton(self.form_tab)
        self.push_query.setObjectName("push_query")
        self.push_query.setText( "Query (Ctrl/Cmd+Enter)")
        self.horizontalLayout.addWidget(self.push_query)
        self.group_form_layout.addLayout(self.horizontalLayout, 1, 1, 1, 1)

        #Add explanation of form
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.form_tab)
        self.plainTextEdit.setAutoFillBackground(False)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit.setPlainText( "The default table for the form is a join of job, relax_job, finaltraj and struct, as well as a left join with the surface, molecule, and bulk tables. If you would like a different join please use the expert mode.\n")
        self.group_form_layout.addWidget(self.plainTextEdit, 0, 0, 2, 1)
        self.tabWidget.addTab(self.form_tab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.form_tab),"SQL Form")
        self.group_query_layout.addWidget(self.tabWidget)
        self.right_frame_layout.addWidget(self.group_query)
        self.query_tab_layout.addWidget(self.right_frame)
        self.right_frame_layout.setStretch(1,1)
        self.query_tab_layout.setStretch(1,1)

        self.central_tabWidget.addTab(self.query_tab,"Query GUI")
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

        valuesUnique = [    str(self.model.record(row).value(self.logicalIndex))
                            for row in range(self.model.rowCount())
                            ]
        if len(set(valuesUnique)) == self.model.rowCount():
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
    sys.argv.append('--disable-web-security')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment(is_pyqtgraph=False))

    gui = JobMakerGUI()
    gui.showMaximized()
    sys.exit(app.exec_())
