#Typing imports
import typing as typ

#External imports
import qdarkstyle                                 # type: ignore
import sqlparse                                   # type: ignore
import time, logging, subprocess, os
from ase.visualize import view                    # type: ignore
from PyQt5 import QtCore, QtGui, QtWidgets, QtSql # type: ignore

#Internal Imports
import catalog.fw.incomplete as inc
from catalog.misc.sql_utils import *
import catalog.jobs.cluster as cluster
from catalog.misc.utilities import merge_dicts, get_cluster, read_into_temp, get_hostname_from_fworker
from catalog.catalog_config import USER,SHERLOCK2_USERNAME,SUNCAT_USERNAME


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent : typ.Any) -> None:
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record : typ.Any)-> None:
        msg = self.format(record)
        self.widget.appendPlainText(msg)

class LaunchForm(QtWidgets.QDialog):
    def __init__(self
                ,fwid_list : typ.List[int]
                ,parent    : typ.Any      = None
                )->None:
        super(LaunchForm, self).__init__()
        self.parent = parent
        self.setupUi()

        self.fwid_list    = fwid_list
        self.old_dicts    = {fwid:inc.lpad.get_fw_dict_by_id(fwid)['spec'] for fwid in fwid_list}
        self.modify_dicts = {fwid:{} for fwid in fwid_list} # type: dict
        self.load_list()
        self.load_table()
        self._connect_signals()

    def _connect_signals(self) -> None:
        #Connect push buttons
        self.push_save.clicked.connect(self._save)
        self.push_undo.clicked.connect(self._undo)
        self.push_view.clicked.connect(self._view)
        self.push_archive.clicked.connect(self._archive)
        self.push_fizzle.clicked.connect(self._fizzle)
        self.push_defuse.clicked.connect(self._defuse)
        self.push_launch.clicked.connect(self.launch)

        self.list.itemSelectionChanged.connect(self.load_table)

    def setupUi(self) -> None:
        """
        Create the UI for the QueryGUI object
        """
        header_font = QtGui.QFont()
        header_font.setPointSize(15)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.finish)
        self.createFormGroupBox()
        #Layour table and list
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem())
        item = self.table.horizontalHeaderItem(0)
        item.setText('Key')
        self.table.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem())
        item = self.table.horizontalHeaderItem(1)
        item.setText('Value')
        font = QtGui.QFont()
        font.setPointSize(20)

        self.list = QtWidgets.QListWidget()
        self.list.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)

        #Make saving button
        self.push_save = QtWidgets.QPushButton('Save')
        self.push_save.setFont(font)
        #Make Undo button
        self.push_undo = QtWidgets.QPushButton('Undo All Changes')
        self.push_undo.setFont(font)
        #Make Undo button
        self.push_view = QtWidgets.QPushButton('View')
        self.push_view.setFont(font)
        #Make Archive button
        self.push_archive = QtWidgets.QPushButton('Archive All')
        self.push_archive.setFont(font)
        #Make Fizzle button
        self.push_fizzle = QtWidgets.QPushButton('Fizzle All')
        self.push_fizzle.setFont(font)
        #Make Defuse button
        self.push_defuse = QtWidgets.QPushButton('Defuse All')
        self.push_defuse.setFont(font)
        #Make Defuse button
        self.push_launch = QtWidgets.QPushButton('Launch All')
        self.push_launch.setFont(font)

        #Setup logger
        self.logTextBox = QPlainTextEditLogger(self)
        # # You can format what is printed to text box
        self.logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().handlers = []
        logging.getLogger().addHandler(self.logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        #Lay stuff out
        table_widget = QtWidgets.QGroupBox()
        table_layout = QtWidgets.QHBoxLayout()
        table_layout.addWidget(self.list)
        table_layout.addWidget(self.table)
        table_layout.addWidget(self.logTextBox.widget)

        table_widget.setLayout(table_layout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(table_widget)
        mainLayout.addWidget(self.push_save)
        mainLayout.addWidget(self.push_undo)
        mainLayout.addWidget(self.push_view)
        self.frame = QtWidgets.QFrame()
        fizzle_archive_layout = QtWidgets.QHBoxLayout()
        fizzle_archive_layout.addWidget(self.push_fizzle)
        fizzle_archive_layout.addWidget(self.push_archive)
        fizzle_archive_layout.addWidget(self.push_defuse)
        fizzle_archive_layout.addWidget(self.push_launch)
        self.frame.setLayout(fizzle_archive_layout)
        mainLayout.addWidget(self.frame)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        logging.info('Welcome!')

    def createFormGroupBox(self)->None:
        self.formGroupBox = QtWidgets.QGroupBox("Launch Form")
        layout = QtWidgets.QFormLayout()

        #Build Walltime spinner
        self.walltime_spin = QtWidgets.QSpinBox()
        self.walltime_spin.setMinimum(0); self.walltime_spin.setMaximum(144);
        self.walltime_spin.setValue(20);
        layout.addRow(QtWidgets.QLabel("Walltime:"), self.walltime_spin)

        #build cluster
        self.cluster_combo = QtWidgets.QComboBox()
        [self.cluster_combo.insertItem(i,name) for i,name in enumerate(list(cluster.cluster_dict.keys())+['Same Cluster']+['Fizzle'])]
        self.cluster_combo.setCurrentIndex(len(cluster.cluster_dict.keys()))
        layout.addRow(QtWidgets.QLabel("Cluster:"), self.cluster_combo)

        self.nodes_spin = QtWidgets.QSpinBox()
        self.nodes_spin.setMinimum(1); self.nodes_spin.setMaximum(6);
        self.nodes_spin.setValue(1);
        layout.addRow(QtWidgets.QLabel("Nodes:"), self.nodes_spin)
        self.formGroupBox.setLayout(layout)

    def load_list(self)->None:
        self.list.clear()
        for fwid in self.fwid_list:
            self.list.addItem(str(fwid))
        self.list.setCurrentRow(0)

    def load_table(self)->None:
        banned_keys = ['inittraj']
        self.table.clearContents()
        if len(self.fwid_list)>0:
            self.table.setRowCount(0)
            banned_keys = ['inittraj']
            selected_fwid = int(self.list.currentItem().text())
            fwid_dict = inc.lpad.get_fw_dict_by_id(selected_fwid)['spec']
            queueadapter = fwid_dict['_queueadapter']
            params = fwid_dict['params']
            merged_dict = merge_dicts([params])
            for key,val in merged_dict.items():
                if not key in banned_keys:
                    currentRowCount = self.table.rowCount()
                    self.table.insertRow(currentRowCount)
                    self.table.setItem(currentRowCount,0, QtWidgets.QTableWidgetItem(str(key)))
                    if self.modify_dicts[selected_fwid].get(key,None):
                        val = self.modify_dicts[selected_fwid].get(key,None)
                    self.table.setItem(currentRowCount,1, QtWidgets.QTableWidgetItem(str(val)))
            self.table.resizeColumnsToContents()

    def _save(self)->None:
        selected_fwid = int(self.list.currentItem().text())
        fw_spec       = inc.lpad.get_fw_dict_by_id(selected_fwid)['spec']
        old_dict      = merge_dicts([fw_spec['params']])
        for i_row in range(self.table.rowCount()):
            key = self.table.item(i_row,0).text()
            val = self.table.item(i_row,1).text()
            old_type = type(old_dict[key])
            if not old_type == str and not old_type == type(None):
                if old_type == list or old_type == bool:
                    val = eval(val)
                else:
                    val = old_type(val)
            if old_type == type(None):
                pass
            elif not val == old_dict[key]:
                logging.info('Changed {} for fwid {} from {} to {}'.format(key,selected_fwid,old_dict[key],val))
                self.modify_dicts[selected_fwid][key] = val

    def _undo(self)->None:
        self.modify_dicts = {fwid:{} for fwid in self.fwid_list}
        self.load_table()

    def _defuse(self)->None:
        for fwid in self.fwid_list:
            inc.lpad.defuse_fw(fwid)

    def _fizzle(self)->None:
        for fwid in self.fwid_list:
            state = inc.lpad.get_fw_dict_by_id(fwid)['state']
            if state in ['RESERVED','RUNNING']:
                inc.fizzle(fwid,force_cancel=True)
            else:
                logging.error('fwid {} can\'t be fizzled it has state: {}'.format(fwid,state))

    def _archive(self)->None:
        for fwid in self.fwid_list:
            inc.archive_by_fwid(fwid)

    def _view(self)->None:
        """
        View a traj file in the launch directory of the selected fireworkself.
        Looks in the current launch directory of the selected fwid and finds the
        non empty traj files. Prompts the user to specify which one they would
        like to view.
        """
        import tempfile
        #Get the selected fwid
        selected_fwid = int(self.list.currentItem().text())
        #Find the launch_dir and cluster of that job
        launch_dir    = self.old_dicts[selected_fwid]['_launch_dir']
        fworker       = self.old_dicts[selected_fwid]['_fworker']
        hostname      = get_hostname_from_fworker(fworker)
        #Find which traj files are not empty in that launch directory
        command       = 'ssh {}@{} find "{}/*.traj" -not -empty -print'.format(USER,hostname,launch_dir)
        output        = subprocess.check_output(command, shell=True)
        traj_files    = output.decode().split('\n')[:-1]
        base_names    = [os.path.basename(file) for file in traj_files]
        #Open up a dialog box to ask the user which file to view
        dialogbox     = QtWidgets.QInputDialog()
        item, ok      = dialogbox.getItem(self, 'Viewer','Select a traj to view:',base_names,0,False)
        #View that traj file
        if item and ok:
            local_path       = read_into_temp(traj_files[base_names.index(item)])
            output           = subprocess.check_output('python -c "from catalog.misc.atoms import smart_view; smart_view(\'{}\')"'.format(local_path),shell=True)
            #Remove the temporary file
            os.remove(local_path)


    def launch(self) -> None:
        clusters_to_launch = []
        walltime    = self.walltime_spin.value()
        clust_str   = self.cluster_combo.currentText()

        logging.info('Rerunning fwids = {}'.format(self.fwid_list))
        nodes       = int(self.nodes_spin.value())
        for fwid in self.fwid_list:
            state   = inc.lpad.get_fw_dict_by_id(fwid)['state']
            if state   == 'DEFUSED' :
                inc.lpad.reignite_fw(fwid)
            elif state == 'RUNNING' :
                logging.error('Can\'t rerun fwid {}, it has state {}'.format(fwid,state))
                continue

            fw_spec = inc.lpad.get_fw_dict_by_id(fwid)['spec']
            fworker   = fw_spec['_fworker']

            if clust_str == 'Same Cluster':
                to_cluster = cluster.cluster_dict[fworker]
            else:
                to_cluster  = cluster.cluster_dict[clust_str]

            if not fworker == to_cluster.name:
                inc.switchCluster(fwid, from_cluster_str = fworker, to_cluster_str = clust_str)

            inc.modify(fwid,'_queueadapter', lambda x: to_cluster.qfunc(walltime,nodes))
            inc.modify_p(fwid,self.modify_dicts[fwid])
            if len(self.modify_dicts[fwid])>0:
                logging.info('Param keys modified for fwid {}: {}'.format(fwid,list(self.modify_dicts[fwid].keys())))

            inc.lpad.rerun_fw(fwid)

            clusters_to_launch.append(to_cluster.name)
        self.launch_rockets(clusters_to_launch)
        self.fwid_list = []
        self.load_list()
        self.load_table()

    def launch_rockets(self, clusters_to_launch : typ.List[str])-> None:
        if 'sherlock2' in clusters_to_launch:
            if not get_cluster() == 'sherlock':
                ssh_command = 'ssh -t {}@login.sherlock.stanford.edu'.format(SHERLOCK2_USERNAME)
                command =['bash','-c',"'$CATALOG_LOC/fireworks/launcher.sh'"]
                p = subprocess.Popen(ssh_command.split()+command,stdout=subprocess.PIPE)
                out, _ = p.communicate()
                logging.info(out.decode())
            else:
                pass
        if 'suncat' in clusters_to_launch:
            ssh_command = 'ssh {}@suncatls1.slac.stanford.edu'.format(SUNCAT_USERNAME)
            command =['bash','-c',"'$CATALOG_LOC/fireworks/launcher.sh'"]
            p = subprocess.Popen(ssh_command.split()+command,stdout=subprocess.PIPE)
            out, _ = p.communicate()
            logging.info(out.decode())

    def finish(self)->None:
        self.parent.central_tabWidget.setCurrentIndex(0)
        self.parent.central_tabWidget.removeTab(1)
        self.accept()
