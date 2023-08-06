# Typing Modules
import typing as typ
if typ.TYPE_CHECKING:
    import pandas as pd  # type: ignore

# External modules
# import sqlite3
import subprocess,math,os,sys,json,warnings, sqlite3
import sql                                        # type: ignore
from sql.aggregate import Sum                     # type: ignore
import ase                                        # type: ignore
import prettytable                                # type: ignore
from ase.visualize import view                    # type: ignore
from ase.data import (atomic_masses, atomic_names # type: ignore
                     ,chemical_symbols, covalent_radii
                     ,reference_states)
from ase.build import bulk, molecule  # type: ignore

# Internal modules
from catalog.misc.utilities import sub_binds
from catalog.misc.print_parse import ask, read_storage_json
from catalog.misc.atoms import make_atoms, json_to_traj
from catalog.misc.sql_utils import *
import catalog.misc.sql_utils as sql_utils
"""
Primary functions for interfacing with main database, $SCRATCH/db/data.db
"""
#################################################################################
# Constants
###########

##########################################################
# QUERY CLASS
##########################################################


realDB = ConnectInfo(host='mysql01.stanford.edu'  # 'g-suncat-suncatdata.sudb.stanford.edu'
                     , port=3306, user='gsuncatsuncatd', passwd='BCe8HzyXCA-ekD!!', db='g_suncat_suncatdata')


class Query(object):
    """
    Read from a SQLite database
    """

    def __init__(self
                ,cols       : typ.List[sql.Column]     = [tbl_relax_job.job_id]
                ,constraints: typ.List[typ.Any]        = []
                ,table      : sql.Table                = tbl_relaxfinal
                ,order      : typ.Optional[sql.Column] = None
                ,group      : typ.Optional[sql.Column] = None
                ,limit      : typ.Optional[int]        = None
                ,connectinfo: ConnectInfo              = realDB
                ,verbose    : bool                     = False
                ,distinct   : bool                     = False
                 ) -> None:

        self.constraints = constraints
        self.cols = cols
        self.table = table
        self.order = order
        self.group = group
        self.limit = limit
        self.connectinfo = connectinfo
        self.verbose = verbose

    def query(self
             ,table      : typ.Optional[sql.Table]   = None
             ,constraints: typ.Optional[list]        = None
             ,cols       : typ.Optional[list]        = None
             ,connectinfo: typ.Optional[ConnectInfo] = None
              ) -> list:
        """ [STRING] -> CONSTRAINT -> [[sqloutput]] """
        if cols is None:
            cols = self.cols
        if table is None:
            table = self.table
        if constraints is None:
            constraints = self.constraints
        if connectinfo is None:
            connectinfo = self.connectinfo

        command = self._command(constraints=constraints,
                                cols=cols, table=table)
        if self.verbose == True:
            sub_binds(command)
        return sqlselect(conn=connectinfo, q=tuple(command)[0].replace('"', '`'), binds=tuple(command)[1])

    def query_dict(self, table: typ.Optional[sql.Table] = None, constraints: typ.Optional[list] = None, cols: typ.Optional[list] = None, connectinfo: typ.Optional[ConnectInfo] = None
                   ) -> list:
        """ [STRING] -> CONSTRAINT -> [{colname:colval}] """
        if cols is None:
            cols = self.cols
        if table is None:
            table = self.table
        if constraints is None:
            constraints = self.constraints
        if connectinfo is None:
            connectinfo = self.connectinfo

        command = self._command(constraints=constraints,
                                cols=cols, table=table)
        if self.verbose == True:
            sub_binds(command)

        return select_dict(conn=connectinfo, q=tuple(command)[0].replace('"', '`'), binds=tuple(command)[1])

    def _command(self
                ,constraints: list
                ,cols       : list
                ,table      : sql.Table
                 ) -> typ.Any:
        if len(cols) == 1 and '*' == str(cols[0]):
            cols = []
        self.last_command = table.select(
            *cols, where=And(constraints), order_by=self.order, limit=self.limit, group_by=self.group)
        return self.last_command

    def query_col(self, col: sql.Column, constraints: typ.Optional[list] = None, table: typ.Optional[sql.Table] = None
                  ) -> list:
        assert isinstance(
            col, sql.Column), 'Please supply a single column (You probably used a singleton list)'
        query_output = self.query(
            cols=[col], constraints=constraints, table=table)
        return [row[0] for row in query_output]

    def make_atoms(self) -> typ.List[ase.Atoms]:
        """returns a list of atoms corresponding to each row in the database"""
        assert 'struct' in table_names(
            self.table), 'The query is not joined to the structure table'
        raw_jsons = self.query_col(tbl_struct.raw)
        return [json_to_traj(json_curr) for json_curr in raw_jsons]

    def view(self
             ) -> None:
        """
        View with ase-gui the initial or final atoms object for a given job - specified by a constraint
        """
        stordirs = self.query_col(tbl_job.stordir)
        output = zip(self.make_atoms(), stordirs)  # type: ignore
        for i, (atoms_obj, storage_directory) in enumerate(output):
            print('#%d/%d stored at: %s' %
                  (i + 1, len(stordirs), storage_directory))
            view(atoms_obj)
            if (i + 1 == len(stordirs)) or 'q' in input():
                break

    def query1(self, col: sql.Column) -> typ.Any:
        output = self.query_col(col)
        if len(output) != 1:
            raise ValueError(
                'query1 did not return one result: ' + str(output))
        return output[0]

    def any_query(self, anycol: sql.Column
                  ) -> bool:
        """
        A column must be specified that is in the table
        """
        return len(self.query_col(anycol)) > 0

    def col_names(self) -> typ.List[str]:
        self.table_names = table_names(self.table)
        col_names = []  # type: list
        for table_name in self.table_names:
            command = "\
                      SELECT `COLUMN_NAME`\
                      FROM `INFORMATION_SCHEMA`.`COLUMNS`\
                      WHERE `TABLE_SCHEMA`='g_suncat_suncatdata'\
                          AND `TABLE_NAME`='%s';\
                      " % (table_name)
            col_names += list(zip(*
                                  sqlselect(conn=self.connectinfo, q=command)))[0]
            # output = [table_name+'.'+col_name for col_name in col_names]
        return list(set(col_names))

    # def dataframe(self)->"pd.DataFrame":
    #     """
    #
    #     """
    #     import pandas as pd
    #     col_names       = map(str,self.cols)
    #     list_of_columns = zip(*self.query())                    # convert rows to columns
    #     df = pd.DataFrame(dict(zip(col_names,list_of_columns))) # match with column names
    #     return df
    #
    # def csv(self,fileout : str ='out.csv') -> None:
    #     import csv
    #     col_names = map(str,self.cols)
    #     rows      = self.query()
    #     with open(fileout, 'w+') as csvfile:
    #         writer = csv.writer(csvfile, delimiter='$',
    #                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #         writer.writerow(col_names)
    #         for row in rows: writer.writerow(row)

    # def query_parent_cols(self
    #                      ,cols              : list
    #                      ,added_constraints : list = []
    #                      ,warn_if_no_parent : bool = True
    #                      ) -> list:
    #     """
    #     Allows the user to query columns from the
    #     If the final_table is being used a
    #     """
    #     assert self.table in [final_table], 'querying parent columns has only been implemented for the final_table in sql'
    #     if None in self.query_col(job.parent) and warn_if_no_parent:
    #         warnings.simplefilter('always', UserWarning)
    #         warnings.warn('Some rows in this query have no parents', UserWarning, stacklevel = 1)
    #
    #     new_constraints = self.constraints + added_constraints
    #     if not isinstance(cols, list):
    #         return self.query_col(cols, constraints = new_constraints, table = parent_child_table)
    #     return self.query(cols = cols, constraints = new_constraints, table = parent_child_table)

    # def ptable(self)->None:
    #
    #     command         = self._command(self.constraints,self.cols,self.table)
    #     connection      = sqlite3.connect(self.db_path)
    #     cursor          = connection.cursor()
    #     if self.verbose: print(tuple(command))
    #     cursor.execute(*tuple(command))
    #     mytable         = prettytable.from_db_cursor(cursor) # type: ignore
    #     cursor.close();connection.close()# type: ignore
    #     print(mytable)
    #     print('Results: %d'%len(mytable._rows))


class AdsEnergyQuery(object):
    """
    Specific query for querying Adsorption Energies

    inner_constraints are applied before the group concat is applied. This can
    (and should) be used to choose the ref_scheme_id, calc comparison parameters,
    and other constraints to limit which ads_triples are legitamate

    outer_constraints are applied to the last select statement, you have access
    to the default columns:
    (bare_id, complex_id,name, bare_name (a job_name), complex_name (a job_name)
    e_ads, job_dict)
    As well as any other columns you add to the inner inner_columns_dict

    inner_columns_dict is in the format {column_alias: table.column}
    The possible tables to query from are listed below along with their variable
    name (see catalog.misc.sql_utils for source code for each variable):

    Description             Table           Varname
    N/A                     ads_triple      T
    Bare finaltraj          finaltraj       BF
    Complex finaltraj       finaltraj       CF
    Bare relax_job          relax_job       BR
    Complex relax_job       relax_job       CR
    Bare job                job             BJ
    Complex job             job             CJ
    Bare struct             struct          BS
    Complex struct          struct          CS
    Bare calc_other         calc_other      BC
    Complex calc_other      calc_other      CC
    ads_eng                 ads_eng         A
    adsorbate job           job             AJ
    Adsorbate calc_other    calc_other      AC
    """

    def __init__(self
                , inner_constraints: typ.List[typ.Any] = []
                , outer_constraints: typ.List[typ.Any] = []
                , inner_columns_dict: typ.Dict[sql.Column
                , str] = {}
                , order: typ.Optional[sql.Column] = None
                , group: typ.Optional[sql.Column] = None
                , limit: typ.Optional[int] = None
                , connectinfo: ConnectInfo = realDB
                , verbose: bool = False
                ) -> None:

        self.inner_constraints = inner_constraints
        self.outer_constraints = outer_constraints
        self.inner_columns_dict = inner_columns_dict
        self.order = order
        self.group = group
        self.limit = limit
        self.connectinfo = connectinfo
        self.verbose = verbose

    def query(self) -> typ.List[tuple]:
        command = self._command()
        if self.verbose == True:
            sub_binds(command)
        return sqlselect(conn=self.connectinfo, q=tuple(command)[0].replace('"', '`'), binds=tuple(command)[1])

    def query_dict(self) -> typ.List[dict]:
        command = self._command()
        if self.verbose == True:
            sub_binds(command)
        return select_dict(conn=self.connectinfo, q=tuple(command)[0].replace('"', '`'), binds=tuple(command)[1])

    def _command(self) -> sql.Select:
        inner_columns = [As(val, key)
                         for key, val in self.inner_columns_dict.items()]
        inner_select = sql_utils.tbl_eads.select(
            *sql_utils.eads_columns_inner + inner_columns, where=And(self.inner_constraints), group_by=sql_utils.eads_group_by_inner)
        outer_select_cols = [inner_select.ref_scheme_id,inner_select.bare_id, inner_select.complex_id, inner_select.name, inner_select.bare_name, inner_select.complex_name, As(inner_select.delta_e_surf - Sum(
            inner_select.energy_norm * inner_select.coef * inner_select.number), 'e_ads'), As(CON('[', GROUPCONCAT(CON('(', inner_select.element_id, ',[', inner_select.jobs, '])')), ']'), 'job_dict')]

        eads_group_by_outer = [inner_select.bare_id, inner_select.complex_id,inner_select.ref_scheme_id]
        added_outer_select_cols = [sql.Column(
            inner_select, name) for name in self.inner_columns_dict.keys()]

        outer_select = inner_select.select(
            *outer_select_cols + added_outer_select_cols, group_by=eads_group_by_outer)
        self.last_command = outer_select.select()
        return self.last_command

    def make_atoms(self
                   ) -> typ.List[dict]:
        tmp_dict = self.inner_columns_dict
        self.inner_columns_dict = {}
        self.inner_columns_dict['ads_raw'] = CON(
            '[', GROUPCONCAT(CON(AS.raw)), ']')
        self.inner_columns_dict['bare_raw'] = BS.raw
        self.inner_columns_dict['complex_raw'] = CS.raw
        query_output = self.query_dict()
        output_list = []
        for row in query_output:
            row_dict = {}
            for raw_name in self.inner_columns_dict.keys():
                if raw_name == 'ads_raw':
                    row[raw_name] = json.loads(row[raw_name])
                    row_dict[raw_name] = [json_to_traj(
                        json.dumps(raw_curr)) for raw_curr in row[raw_name]]
                else:
                    row_dict[raw_name] = json_to_traj(str(row[raw_name]))
            output_list.append(row_dict)
        self.inner_columns_dict = tmp_dict
        return output_list

    def view(self, view_refs: bool = False
             ) -> None:
        output_atom_dicts = self.make_atoms()
        output_row_dicts = self.query_dict()
        for i, (atoms_dict, row_dict) in enumerate(zip(output_atom_dicts, output_row_dicts)):
            print('#%d/%d' % (i + 1, len(output_atom_dicts)))
            print(self._row_dict_summary(row_dict))
            flattened_list = [atoms_dict['bare_raw'],
                              atoms_dict['complex_raw']]
            if view_refs:
                view(atoms_dict['ads_raw'] + flattened_list)
            else:
                view(flattened_list)
            if (i + 1 == len(output_atom_dicts)) or 'q' in input():
                break

    @staticmethod
    def _row_dict_summary(row_dict: dict, summary_keys: list = ['bare_name', 'complex_name', 'e_ads', 'bare_id', 'complex_id']
                          ) -> str:

        lines = ['{0} : {1}'.format(key, val) if key in summary_keys else '' for key,
                 val in row_dict.items() if key in summary_keys]
        return '\n'.join(lines)


###################
# Interface with DB
# ------------------
def sqlite_execute(db_path: str, sqlcommand: str, binds: list = []
                   ) -> None:
    """
    Execute a SQL statement that modifies the database
    """
    assert sqlcommand.lower()[:6] != 'select'
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(sqlcommand, binds)
        output_array = cursor.fetchall()
        conn.commit()


def sqlite_select(db_path: str, sqlcommand: str, binds: list = [], mk_dict: bool = False
                  ) -> list:
    """
    Select and return a list of tuples
    """
    def dict_factory(cursor, row):  # type: ignore
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    assert sqlcommand.lower()[:6] == 'select'

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        if mk_dict:
            cursor.row_factory = dict_factory

        cursor.execute(sqlcommand, binds)
        output_array = cursor.fetchall()
    return output_array


def select_dict(conn: ConnectInfo, q: str, binds: list = []
                ) -> typ.List[dict]:
    #print('selecting dict ',q)
    with conn.mk_conn(mk_dict=True) as cxn:  # type: ignore
        if 'group_concat' in q.lower():
            cxn.execute("SET SESSION group_concat_max_len = 100000")
        cxn.execute(q, args=binds)
        return cxn.fetchall()


def sqlselect(conn: ConnectInfo, q: str, binds: list = []
              ) -> typ.List[tuple]:
    # print('\n\nSQLSELECT ',q)#,binds)
    with conn.mk_conn() as cxn:  # type: ignore
        if 'group_concat' in q.lower():
            cxn.execute("SET SESSION group_concat_max_len = 100000")
        cxn.execute(q, args=binds)
        return cxn.fetchall()


def sqlexecute(conn: ConnectInfo, q: str, binds: list = []
               ) -> None:
    print('\n\nSQLEXECUTE ', q)  # ,binds)
    with conn.mk_conn() as cxn:  # type: ignore
        cxn.execute("SET SESSION auto_increment_offset = 1")
        cxn.execute("SET SESSION auto_increment_increment = 1")
        cxn.execute(q, args=binds)


def sqlexecutemany(conn: ConnectInfo, q: str, binds: typ.List[list]
                   ) -> None:
    print('executemany Q: ', q, binds)
    with conn.mk_conn() as cxn:  # type: ignore
        cxn.executemany(q, args=binds)


###################
# MODIFY Functions
###################
def iif(a, b, c): return b if a else c  # type: ignore


###########
# def sqlexecute(sqlcommand, binds = [],db_path=dbreal,row_factory=None,hacks = []): # type: ignore
#     assert sqlcommand.lower()[:6] in ['create','select','insert','delete','alter ','update','drop t'], "Sql Query weird "+sqlcommand
#     connection = sqlite3.connect(db_path,timeout=30)
#     if 'sqrt' in sqlcommand: connection.create_function('SQRT',1,math.sqrt)
#
#     for h in hacks: sqlcommand = h(sqlcommand) # apply hacks to string
#
#     cursor     = connection.cursor()
#     cursor.row_factory = row_factory
#     cursor.execute(sqlcommand, binds)
#     output_array = cursor.fetchall()
#
#
#     if sqlcommand.lower()[:6] != 'select': connection.commit()
#     connection.close()
#     return output_array
#
# def sqlexecutemany(sqlcommand, binds = [],db_path=dbreal): # type: ignore
#     assert sqlcommand.lower()[:6] in ['create','select','insert','delete','alter ','update'], "Sql Query weird "+sqlcommand
#     connection  = sqlite3.connect(db_path,timeout=60)
#     cursor      = connection.cursor()
#     cursor.executemany(sqlcommand, binds)
#     if 'select' not in sqlcommand.lower(): connection.commit()
#     cursor.close() # type: ignore
#     connection.close()
#     return

# def updateDB(set_column : str
#             ,id_column  : str
#             ,ID         : int
#             ,new_value  : typ.Any
#             ,table      : str
#             ,db_path    : str     =dbreal
#             ) -> None:
#     """
#     """
#     sqlexecute("UPDATE {0} SET {1}= ? WHERE {2} = ?".format(table,set_column,id_column),[new_value,ID],db_path=db_path)# type: ignore
#
# def drop_table(tableName : str
#               ,db_path   : str =dbreal
#               ) -> None:
#     """
#     """
#     print('dropping table ',tableName)
#     try: sqlexecute("DROP TABLE %s"%tableName,db_path=db_path) # type: ignore
#     except Exception as e: print('\tdrop_table exception: ',e)
# def deleteRow(tableName : str
#              ,idColumn  : str
#              ,ID        : int
#              ,db_path   : str = '/scratch/users/ksb/share/suncatdata.db'
#              ) -> None:
#     """
#     """
#     sqlexecute("DELETE FROM {0} WHERE {1} = {2}".format(tableName,idColumn,ID),db_path=db_path) # type: ignore
#
# def addCol(colname   : str
#           ,coltype   : str
#           ,tableName : str
#           ,db_path   : str
#           ) -> None:
#     sqlexecute("ALTER TABLE {0} ADD COLUMN {1} {2}".format(tableName,colname,coltype),db_path=db_path)# type: ignore

###################
# Creating/deleting
###################
# def get_max(tab: str, col: str, db_path: str
#             ) -> int:
#     """
#     """
#     cmd = 'SELECT {0} FROM {1} ORDER BY {0} DESC LIMIT 1'
#     args = [col, tab]
#     return sqlexecute(cmd.format(*args), db_path=db_path)[0][0]  # type: ignore
#
#
# def removeSuncatDataDB(db_path: str ='/scratch/users/ksb/share/temp.db') -> None:
#     """
#     """
#     print("removing ", db_path)
#     if os.path.exists(db_path):
#         os.remove(db_path)
#
#
# def createSuncatDataDB(db_path: str ='/scratch/users/ksb/share/temp.db') -> int:
#     print('creating DB at ', db_path)
#
#     fill_element(db_path)
#
#     sqlexecute(('CREATE TABLE atom        (id     integer primary key'  # type: ignore
#                 + ',atoms_id    integer not null'
#                 + ',ind         integer not null'
#                 + ',number      integer not null'
#                 + ',x           numeric not null'
#                 + ',y           numeric not null'
#                 + ',z           numeric not null'
#                 + ',constrained integer not null'
#                 + ',magmom      numeric not null'
#                 #+',tag         integer'
#                 # don't want 2 rows describing same index of same Atoms object
#                 + ',UNIQUE (atoms_id,ind)'
#                 + ',FOREIGN KEY(number) REFERENCES element(id)'
#                 + ',FOREIGN KEY(atoms_id) REFERENCES atoms(id))'), db_path=db_path)
#
#     sqlexecute(("CREATE TABLE cell     (id     integer primary key"  # type: ignore
#                 + ',ax numeric not null'
#                 + ',ay numeric not null'
#                 + ',az numeric not null'
#                 + ',bx numeric not null'
#                 + ',by numeric not null'
#                 + ',bz numeric not null'
#                 + ',cx numeric not null'
#                 + ',cy numeric not null'
#                 + ',cz numeric not null'
#                 + ',UNIQUE(ax,ay,az,bx,by,bz,cx,cy,cz))'), db_path=db_path)
#
#     sqlexecute(("CREATE TABLE atoms     (id     integer primary key"  # type: ignore
#                 + ',cell_id integer not null'
#                 + ',FOREIGN KEY(cell_id) REFERENCES cell(id))'), db_path=db_path)
#
#     sqlexecute(("CREATE TABLE calc        (id  integer primary key"  # type: ignore
#                 + ',dftcode  varchar not null'
#                 + ',xc       varchar'
#                 + ',pw       integer'
#                 + ',kpts     varchar'
#                 + ',fmax     numeric'
#                 + ',psp      varchar'
#                 + ',econv    numeric'
#                 + ',xtol     numeric'
#                 + ',strain   numeric'
#                 + ',dw       integer'
#                 + ',sigma    numeric'
#                 + ',nbands   integer'
#                 + ',mixing   numeric'
#                 + ',nmix     integer'
#                 + ',gga      varchar'
#                 + ',luse_vdw integer'
#                 + ',zab_vdw  numeric'
#                 + ',nelmdl   integer'
#                 + ',gamma    integer'
#                 + ',dipol    varchar'
#                 + ',algo     varchar'
#                 + ',ibrion   integer'
#                 + ',prec     varchar'
#                 + ',ionic_steps integer'
#                 + ',lreal    varchar'
#                 + ',lvhar    integer'
#                 + ',diag     varchar'
#                 + ',spinpol  integer'
#                 + ',dipole   integer'
#                 + ',maxstep  integer'
#                 + ',delta    numeric'
#                 + ',mixingtype varchar'
#                 + ',bonded_inds varchar'
#                 + ',energy_cut_off numeric'
#                 + ',step_size numeric'
#                 + ',springs varchar'
#                 + ',UNIQUE(dftcode,xc,pw,kpts,fmax,psp,econv,xtol,strain,dw,sigma,nbands,mixing,nmix,gga,luse_vdw,zab_vdw,nelmdl,gamma,dipol,algo,ibrion,prec,ionic_steps'
#                 + ',lreal,lvhar,diag,spinpol,dipole,maxstep,delta,mixingtype,bonded_inds,energy_cut_off,step_size,springs))'), db_path=db_path)
#
#     sqlexecute("CREATE TABLE job          (id                integer primary key"  # type: ignore
#                + ',deleted           integer not null'
#                + ',user              varchar not null'
#                + ',timestamp         numeric not null'
#                + ',working_directory varchar not null unique'
#                + ',storage_directory varchar not null unique'
#                + ',job_name          varchar not null '
#                + ',guess_jobtype     varchar not null '
#                + ',calc_id           integer not null '
#                + ',initatoms         integer not null '
#                + ',finalatoms        integer not null '
#                + ',FOREIGN KEY(calc_id)    REFERENCES calc  (id)'
#                + ',FOREIGN KEY(initatoms)  REFERENCES atoms (id)'
#                + ',FOREIGN KEY(finalatoms) REFERENCES atoms (id))', db_path=db_path)
#
#     # sqlexecute("CREATE TABLE keyword      (id integer primary key"  # type: ignore
#     #                                    +',job_id integer not null unique'
#     #                                    +',FOREIGN KEY(job_id) REFERENCES job (id))',db_path=db_path)
#
#     sqlexecute("CREATE TABLE composition (id integer primary key"  # type: ignore
#                + ',element_id integer not null '
#                + ',atoms_id   integer not null '
#                + ',has        integer not null '
#                + ',UNIQUE (element_id,atoms_id)'
#                + ',FOREIGN KEY(element_id) REFERENCES element (id)'
#                + ',FOREIGN KEY(atoms_id) REFERENCES atoms (id))', db_path=db_path)
#
#     fill_element(db_path)
#     add_refstoich(db_path)
#     add_refeng(db_path)
#     os.system('chmod 777 ' + db_path)
#     return 1


###################
# Supplementary
# ----------------
# def add_refeng(db_path: str =dbreal) -> None:
#     sqlexecute("CREATE TABLE refeng      (id integer primary key"  # type: ignore
#                + ',element_id integer not null '
#                + ',calc_id integer not null '
#                # this isn't property of calculator so it must be appended here
#                + ',kptden_x numeric not null '
#                # this isn't property of calculator so it must be appended here
#                + ',kptden_y numeric not null '
#                + ',UNIQUE (element_id,calc_id)'
#                + ',FOREIGN KEY(element_id) REFERENCES element (id)'
#                + ',FOREIGN KEY(calc_id) REFERENCES calc (id))', db_path=db_path)
#
#
# def add_refstoich(db_path: str =dbreal) -> None:
#     sqlexecute("CREATE TABLE refstoich (id integer primary key"  # type: ignore
#                + ',reference_element integer'
#                + ',component_element integer'
#                + ',component_weight  numeric'
#                + ',total_components  integer'
#                + ',FOREIGN KEY(reference_element) REFERENCES element (id)'
#                + ',FOREIGN KEY(component_element) REFERENCES element (id))', db_path=db_path)
#     cols = 'reference_element,component_element,component_weight,total_components'
#     for i in range(1, 119):
#         if i == 6:
#             sqlexecute('INSERT into refstoich (%s) VALUES (?,?,?,?)' %
#                        cols, [i, i, 1, 3], db_path)  # type: ignore
#             sqlexecute('INSERT into refstoich (%s) VALUES (?,?,?,?)' %
#                        cols, [6, 8, -1, 3], db_path)  # type: ignore
#             sqlexecute('INSERT into refstoich (%s) VALUES (?,?,?,?)' %
#                        cols, [6, 1, 2, 3], db_path)  # type: ignore
#         elif i == 8:
#             sqlexecute('INSERT into refstoich (%s) VALUES (?,?,?,?)' %
#                        cols, [i, i, 1, 2], db_path)  # type: ignore
#             sqlexecute('INSERT into refstoich (%s) VALUES (?,?,?,?)' %
#                        cols, [8, 1, -2, 2], db_path)  # type: ignore
#         else:
#             sqlexecute('INSERT into refstoich (%s) VALUES (?,?,?,?)' %
#                        cols, [i, i, 1, 1], db_path)  # type: ignore
#
#
# def add_element(db_path: str =dbreal) -> None:
#     sqlexecute(("CREATE TABLE element   (id     integer primary key"   # type: ignore
#                 + ',symbol  varchar not null'
#                 + ',name    varchar not null'
#                 + ',mass    numeric not null'
#                 + ',radius  numeric not null'
#                 + ',reference_phase varchar'
#                 + ',reference_spacegroup integer '
#                 + ',reference_pointgroup varchar'
#                 # brian's columns
#                 + ',atomic_number                integer'
#                 + ',atomic_weight                numeric'
#                 + ',abundance_crust              numeric'
#                 + ',abundance_sea                numeric'
#                 + ',atomic_radius                numeric'
#                 + ',atomic_volume                numeric'
#                 + ',atomic_weight_uncertainty    numeric'
#                 + ',boiling_point                numeric'
#                 + ',covalent_radius_bragg        numeric'
#                 + ',covalent_radius_cordero      numeric'
#                 + ',covalent_radius_pyykko       numeric'
#                 + ',covalent_radius_pyykko_double   numeric'
#                 + ',covalent_radius_pyykko_triple   numeric'
#                 + ',covalent_radius_slater   numeric'
#                 + ',density                  numeric'
#                 + ',dipole_polarizability    numeric'
#                 + ',econf                    numeric'
#                 + ',electron_affinity    numeric'
#                 + ',en_allen             numeric'
#                 + ',en_ghosh             numeric'
#                 + ',en_pauling           numeric'
#                 + ',evaporation_heat     numeric'
#                 + ',fusion_heat          numeric'
#                 + ',gas_basicity         numeric'
#                 + ',geochemical_class    varchar'
#                 + ',goldschmidt_class    varchar'
#                 + ',group_id             integer'
#                 + ',heat_of_formation    numeric'
#                 + ',is_radioactive       bool'
#                 + ',lattice_constant     numeric'
#                 + ',lattice_structure    varchar'
#                 + ',melting_point        numeric'
#                 + ',metallic_radius      numeric'
#                 + ',metallic_radius_c12  numeric'
#                 + ',period               integer'
#                 + ',proton_affinity      numeric'
#                 + ',thermal_conductivity numeric'
#                 + ',vdw_radius   numeric)'), db_path=db_path)
#
#
# def fill_element(db_path: str = dbreal) -> None:
#
#     add_element(db_path)
#
#     # Constants
#     # ---------
#     sym_dict = {'fcc': 225, 'diamond': 227, 'bcc': 229, 'hcp': 194, 'sc': 221, 'cubic': None, 'rhombohedral': None,
#                 'tetragonal': None, 'monoclinic': None, 'orthorhombic': None, 'diatom': 'D*h', 'atom': 'K*h'}
#
#     ase_cols = ['symbol', 'name', 'mass', 'radius', 'reference_phase',
#                 'reference_spacegroup', 'reference_pointgroup']
#     mendeleev_cols = ['atomic_number', 'atomic_weight', 'abundance_crust', 'abundance_sea', 'atomic_radius', 'atomic_volume',
#                       'atomic_weight_uncertainty', 'boiling_point', 'covalent_radius_bragg', 'covalent_radius_cordero', 'covalent_radius_pyykko',
#                       'covalent_radius_pyykko_double', 'covalent_radius_pyykko_triple', 'covalent_radius_slater', 'density', 'dipole_polarizability',
#                       'econf', 'electron_affinity', 'en_allen', 'en_ghosh', 'en_pauling', 'evaporation_heat', 'fusion_heat', 'gas_basicity', 'geochemical_class',
#                       'goldschmidt_class', 'group_id', 'heat_of_formation', 'is_radioactive', 'lattice_constant', 'lattice_structure', 'melting_point',
#                       'metallic_radius', 'metallic_radius_c12', 'name', 'period', 'proton_affinity', 'symbol', 'thermal_conductivity', 'vdw_radius']
#     cols = ase_cols + mendeleev_cols
#
#     with open(os.environ['HOME'] + '/CataLog/data/element.json', 'r') as f:
#         eledicts = json.load(f)
#
#     binds = []
#     qmarks = ','.join(['?'] * len(cols))
#
#     # Main Loop
#     # ----------
#     for i in range(1, 119):
#         s, n, m, r = [x[i] for x in [chemical_symbols,
#                                      atomic_names, atomic_masses, covalent_radii]]
#         if reference_states[i] is None:
#             rp, rsg, rpg = None, None, None
#         elif 'a' in reference_states[i]:
#             rp, rpg = 'bulk', None
#             rsg = sym_dict[reference_states[i]['symmetry']]
#             if i == 50:
#                 rsg = 227  # ase doesn't think tin is diamond
#         else:
#             rp, rsg = 'molecule', None
#             rpg = sym_dict[reference_states[i]['symmetry']]
#         ase_binds = [s, n, m, r, rp, rsg, rpg]
#
#         m_binds = [eledicts[i - 1].get(m_c) for m_c in mendeleev_cols]
#
#         binds.append(ase_binds + m_binds)
#
#     sqlexecutemany('INSERT INTO element (%s) VALUES (%s)' %
#                    (','.join(cols), qmarks), binds, db_path)  # type: ignore
#
#     return None
#
# ####################
# # MODIFYING STORAGE
# ####################
#
#
# def modify_storage_directory(constraint, file_name, key, value, verbose=True, check=True, dict_loc='params'):  # type: ignore
#
#     def writeOnSherOrSlac(pth, file_text):  # type: ignore
#         if 'scratch' in pth:
#             open(pth, 'w').close()
#             with open(pth, 'w') as f:
#                 return f.write(file_text)
#         elif 'nfs' in pth:
#             writer = subprocess.Popen(['ssh', '{0}@suncatls1.slac.stanford.edu'.format(
#                 user), 'cat -> %s' % (pth)], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
#             writer.stdin.write(file_text)
#             return 1
#         else:
#             raise NotImplementedError('New cluster? path =' + pth)
#
#     # Define protected keys that cannot be changed
#     protected_params = ['kpts', 'jobkind', 'xc', 'maxstep', 'nbands', 'dftcode', 'dwrat', 'kptden', 'finaltraj_pckl', 'finalmagmom_pckl', 'spinpol',
#                         'forces_pckl', 'finalcell_pckl', 'fmax', 'mixing', 'dw', 'psp', 'econv', 'pw', 'nmix', 'finalpos_pckl', 'raw_energy', 'inittraj_pckl', 'sigma']
#     assert key not in protected_params, 'Cannot change job results or calculation parameters in finished jobs'
#     # Define acceptable files to change
#     assert file_name in [
#         'result.json', 'params.json'], 'Can only modify param.json and result.json'
#     # Grab directories that match constraints
#     additionalConstraint = USER_(user)  # type: ignore
#     query = Query(verbose=True, constraints=AND(
#         additionalConstraint, *constraint))
#     directories = query.query_col(STORDIR)
#
#     def modify_dict(curr_dict, key, value, dict_loc):  # type: ignore
#         if not key in curr_dict.keys():
#             if check and ask('Do you want to add new key "{0}" to '.format(key) + file_name):
#                 print('Modifying file: {0}'.format(directory + file_name))
#                 print('Changing {0} parameter: {1}; From {2} to {3}'.format(
#                     dict_loc, key, curr_dict.get(key, "empty"), value))
#                 curr_dict[key] = value
#                 writeOnSherOrSlac(directory + file_name,
#                                   json.dumps(curr_params))   # type: ignore
#         else:
#             print('Modifying file: {0}'.format(directory + file_name))
#             print('Changing {0} parameter: {1}; From {2} to {3}'.format(
#                 dict_loc, key, curr_dict.get(key, "empty"), value))
#             curr_dict[key] = value
#         return curr_dict
#
#     # Iterate through directories and change the value matching the key provided
#     for directory in directories:
#         curr_params = read_storage_json(
#             directory + file_name)  # Get Current Params
#         # Need to check if key in keyword table as they don't exist in curr_params.keys()
#         if dict_loc in ['kwarg', 'project']:
#             curr_dict = json.loads(curr_params.get(
#                 dict_loc)) if dict_loc in curr_params.keys() else {}  # type: ignore
#             assert isinstance(
#                 curr_dict, dict), 'Current parameter value for dict_loc is not a dictionary'  # type: ignore
#             if not curr_dict.get(key) == value:
#                 new_dict = modify_dict(
#                     curr_dict, key, value, dict_loc)  # type: ignore
#                 curr_params[dict_loc] = json.dumps(
#                     new_dict)             # type: ignore
#                 writeOnSherOrSlac(directory + file_name,
#                                   json.dumps(curr_params))  # type: ignore
#         elif dict_loc == 'params':
#             # type: ignore
#             if not curr_params.get(key) == value:
#                 curr_params = modify_dict(
#                     curr_params, key, value, dict_loc)      # type: ignore
#                 writeOnSherOrSlac(directory + file_name,
#                                   json.dumps(curr_params))   # type: ignore
#         else:
#             raise NotImplementedError('Specified dict_loc: {0} has not been made before, please add to the list {1}'.format(
#                 dict_loc, ['kwarg', 'project', 'params']))
