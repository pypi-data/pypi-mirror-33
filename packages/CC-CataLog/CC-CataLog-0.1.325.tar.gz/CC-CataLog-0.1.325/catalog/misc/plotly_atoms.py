#Typing imports
import typing as typ
from typing import Tuple,List

#External imports
import plotly.plotly as py                  # type: ignore
import plotly.graph_objs as go              # type: ignore
from plotly.plotly import plot as onlineplot
from plotly.offline import plot as off_plot # type: ignore
from plotly.grid_objs import Grid, Column   # type: ignore

import itertools,os,sys,time
import ase,ase.io #type: ignore
from copy import deepcopy
import numpy as np #type: ignore
from ase.data import covalent_radii, atomic_numbers #type: ignore

#Internal Imports
from catalog.misc.utilities import merge_dicts
from catalog.misc.atoms import get_list_of_fixed_indices


"""
Construct Plotly objects from atoms objects
"""

################################################################################
# Constnats
#-----------
user = os.environ['USER']


#########################################################
class PlotlyAtoms(object):
    """
    Object for creating atoms objects and theircorresponding network graphs
    """

    def __init__(self
                ,atoms_obj     : ase.Atoms
                ,show_indices  : List[int]      = []
                ,repeat        : Tuple[int,int] = (1,1)
                ) -> None:
        #Assertions for input data
        """
        IN FUTURE, STORE CELL AS ATTRIBUTE TO GRAPH, ALL OTHER INFO IN NODES
            SO THAT WE DONT HAVE TO PASS AN *ATOMS* OBJECT HERE
        """

        #Set member data
        self.atoms                  = atoms_obj
        self.cell                   = atoms_obj.cell


        posTuples = zip(*[x for x in self.atoms.positions])
        self.Xn, self.Yn, self.Zn   = [list(x) for x in posTuples] # convert tuple to list

        #Chemical Info
        self.atomic_numbers         = [atom.number for atom in self.atoms]
        self.chemical_symbols       = [atom.symbol for atom in self.atoms]
        self.chemical_formula       = ''.join([symb+str(self.chemical_symbols.count(symb))
                                                  for symb in np.sort(list(set(self.chemical_symbols)))])

        #Visualization Parameters
        self.repeat                 = repeat
        if show_indices is None:
            self.show_indices       = list(range(len(self.Xn)))
        else:
            if -1 in show_indices:
                show_indices.append(len(self.Xn)-1)
            self.show_indices       = show_indices

        #Create traces and layout
        self.set_grid_data()
        self.data                   = {} # type: dict
        self.edge_trace             = [] #self.get_edge_trace()
        self.node_trace             = self.get_node_trace()
        self.data                   = self.node_trace+self.edge_trace
        self.set_layout()


    def set_grid_data(self,size_factor : int = 80) -> None:
        """
        Helpful docstring from mike
        """
        self.colors = ['rgb({},{},{})'.format(*jmol_colors[x]*255) for x in self.atomic_numbers]
        self.size   = [covalent_radii[atomic_numbers[symb]]*size_factor for symb in self.chemical_symbols]
        self.text   = self.get_atom_labels()
        self.fixed_inds  = get_list_of_fixed_indices(self.atoms)

        for x_shift in range(self.repeat[0])[1:]:
            for y_shift in range(self.repeat[1])[1:]:
                shift = np.dot([x_shift,y_shift,0], self.cell)
                self.Xn+=[x + shift[0] for x in self.Xn]
                self.Yn+=[y + shift[1] for y in self.Yn]
                self.Zn+=[z + shift[2] for z in self.Zn]

        # self.Xe,self.Ye,self.Ze               = [],[],[] # type: Tuple[list,list,list]
        # counted_edges,edge_labels,edge_colors = [],[],[] # type: Tuple[list,list,list]
        #
        # for x_shift in range(self.repeat[0]):
        #     for y_shift in range(self.repeat[1]):
        #         shift = np.dot([x_shift,y_shift,0], self.cell)
        #         for (i,j) in list(set(self.graph.edges())):
        #             if i in self.show_indices or j in self.show_indices:
        #                 if i not in self.show_indices:
        #                     temp = i; i = j; j = temp
        #                 counts = self.graph.get_edge_data(i,j).keys()
        #                 for count in counts:
        #                     edge_dict = self.graph.get_edge_data(i,j)[count]
        #                     edge_color = self.get_red_blue_color(edge_dict.get('bondorder',None))
        #                     edge_colors+= [edge_color]*3
        #                     counted_edges.append((i,j))
        #                     edge_label = [str((i,j))] + [str(edge_dict.get(key,'')) for key in ['bondorder','weight']]
        #                     edge_labels += ['edge pair: {0} <br> bond order: {1} <br> distance: {2}'.format(*edge_label)]*3
        #
        #                     pbc_shift = self._get_pbc_shift(i, j, count)
        #                     real_dis_shift = np.dot(pbc_shift,self.cell)
        #                     self.Xe += [self.Xn[i]+shift[0],self.Xn[j]+real_dis_shift[0]+shift[0],None]# x-coordinates of edge ends
        #                     self.Ye += [self.Yn[i]+shift[1],self.Yn[j]+real_dis_shift[1]+shift[1],None]# y-coordinates of edge ends
        #                     self.Ze += [self.Zn[i]+shift[2],self.Zn[j]+real_dis_shift[2]+shift[2],None]# z-coordinates of edge ends



        # self.grid = Grid([Column(self.Xn,'Xn')])
        # self.grid.append(Column(self.Yn,'Yn'))
        # self.grid.append(Column(self.Zn,'Zn'))
        # self.grid.append(Column(text,'node_text'))
        # self.grid.append(Column(size,'node_size'))
        # self.grid.append(Column(colors,'node_color'))
        # url = py.grid_ops.upload(self.grid, 'grid_data_plotly_'+str(time.time()), auto_open=False)

    def get_atom_labels(self) -> List[str]:
        atom_indices_label      = ['Index: {0}'.format(x) for x in range(len(self.atoms))]
        symbols_label           = ['Symbol: {0}'.format(x) for x in self.chemical_symbols]

        # coordination_num_label  = ['Coord #: {0}'.format(x) for _,x in self.graph.degree()]

        text = ['<br>'.join(string) for string in  zip(atom_indices_label,symbols_label)]
        return text



    def _get_pbc_shift(self,ind_1 : int ,ind_2 : int ,count : int) -> Tuple[int,int,int]:
        from copy import deepcopy
        pbc_shift = (0,0,0)#np.array(self.graph[ind_1][ind_2][count]['pbc_shift'])
        if not ind_1 == ind_2:
            dis_best = np.inf
            for x_mult in [-1,0,1]:
                for y_mult in [-1,0,1]:
                    for z_mult in [-1,0,1]:
                        pbc_shift_curr = deepcopy(pbc_shift)
                        pbc_shift_curr[0] = x_mult; pbc_shift_curr[1] = y_mult; pbc_shift_curr[2] = z_mult
                        dis_shift = np.dot(pbc_shift_curr, self.cell)
                        pos_1   = np.array([self.Xn[ind_1],self.Yn[ind_1],self.Zn[ind_1]])
                        pos_2   = np.array([self.Xn[ind_2],self.Yn[ind_2],self.Zn[ind_2]])
                        dis_curr = np.linalg.norm(dis_shift+pos_2-pos_1)
                        if dis_curr < dis_best:
                            dis_best = dis_curr
                            pbc_shift_best = pbc_shift_curr
        else:
            pbc_shift_best = pbc_shift
        return pbc_shift_best

    @staticmethod
    def get_red_blue_color(value):
        """Convert value between 0 and 1 into an rgb color
        0 will be blue; 1 will be red"""
        if not value==None:
            return 'rgb({0},0,{1})'.format(255*value,255*(1-value))
        else:
            return 'rgb(0,0,0)'

    def get_node_trace(self):
        node_trace = go.Scatter3d(mode = 'markers',
                                  x=self.Xn,
                                  y=self.Yn,
                                  z=self.Zn,
                                  name='Nodes',
                                  marker=dict(symbol='circle',
                                             size=self.size,
                                             sizemin = self.size,
                                             sizeref = 1,
                                             sizemode = 'diameter',
                                             color=self.colors,
                                             line=go.Line(color='rgb(0,0,0)', width=1),
                                             opacity=1
                                             ),
                                  text=self.text,
                                  hoverinfo='text'
                                  )
        cons_trace = go.Scatter3d(mode = 'markers',
                                  x=[xn for i,xn in enumerate(self.Xn) if i in self.fixed_inds],
                                  y=[yn for i,yn in enumerate(self.Yn) if i in self.fixed_inds],
                                  z=[zn for i,zn in enumerate(self.Zn) if i in self.fixed_inds],
                                  name='Nodes',
                                  marker=dict(symbol='x',
                                             size=[size/10 for i, size in enumerate(self.size) if i in self.fixed_inds],
                                             sizeref = 1,
                                             sizemode = 'diameter',
                                             color='rgb(0,0,0)',
                                             line=go.Line(color='rgb(0,0,0)', width=1),
                                             opacity=1
                                             )
                                  )
        return [node_trace,cons_trace]

    def get_edge_trace(self):
        edge_trace = go.Scatter3d(
                            xsrc=self.grid.get_column_reference('Xe'),
                            ysrc=self.grid.get_column_reference('Ye'),
                            zsrc=self.grid.get_column_reference('Ze'),
                            mode='lines',
                            line=go.Line(colorsrc=self.grid.get_column_reference('edge_colors'), width=8),
                            textsrc = self.grid.get_column_reference('edge_labels'),
                            hoverinfo =  "text"
                            )
        return [edge_trace]

    def set_layout(self):

        axis=dict(showbackground= False,
                  showline      = True,
                  zeroline      = True,
                  showgrid      = True,
                  showticklabels= True,
                  autorange     = True
                  )
        x_axis = merge_dicts([{'title':'X'},axis])
        y_axis = merge_dicts([{'title':'Y'},axis])
        z_axis = merge_dicts([{'title':'Z'},axis])

        self.layout = go.Layout(dragmode = "turntable"
                        ,width=2000
                        ,height=800
                        ,showlegend=False
                        ,scene=go.Scene(xaxis=go.XAxis(x_axis)
                                    ,yaxis=go.YAxis(y_axis)
                                    ,zaxis=go.ZAxis(z_axis)
                                    )
                        ,margin=go.Margin(t=100)
                        ,hovermode='closest'
                        )

    def plot(self
            , file_name        = 'atoms_obj.html'
            , include_plotlyjs = False
            , output_type      ='div'
            , offline          = True):
        fig=go.Figure(data=self.data, layout=self.layout)
        if offline:
            output = off_plot(fig,auto_open = False,include_plotlyjs = include_plotlyjs, output_type ='div')
            return output
        else:
            output = onlineplot(fig, auto_open = False, sharing = 'public', filename = file_name)

    def get_figure(self):
        fig=go.Figure(data=self.data, layout=self.layout)


# Jmol colors.  See: http://jmol.sourceforge.net/jscolors/#color_U
jmol_colors = np.array([
(1.000,0.000,0.000) ,# None
(1.000,1.000,1.000), # H
(0.851,1.000,1.000), # He
(0.800,0.502,1.000), # Li
(0.761,1.000,0.000), # Be
(1.000,0.710,0.710), # B
(0.565,0.565,0.565), # C
(0.188,0.314,0.973), # N
(1.000,0.051,0.051), # O
(0.565,0.878,0.314), # F
(0.702,0.890,0.961), # Ne
(0.671,0.361,0.949), # Na
(0.541,1.000,0.000), # Mg
(0.749,0.651,0.651), # Al
(0.941,0.784,0.627), # Si
(1.000,0.502,0.000), # P
(1.000,1.000,0.188), # S
(0.122,0.941,0.122), # Cl
(0.502,0.820,0.890), # Ar
(0.561,0.251,0.831), # K
(0.239,1.000,0.000), # Ca
(0.902,0.902,0.902), # Sc
(0.749,0.761,0.780), # Ti
(0.651,0.651,0.671), # V
(0.541,0.600,0.780), # Cr
(0.612,0.478,0.780), # Mn
(0.878,0.400,0.200), # Fe
(0.941,0.565,0.627), # Co
(0.314,0.816,0.314), # Ni
(0.784,0.502,0.200), # Cu
(0.490,0.502,0.690), # Zn
(0.761,0.561,0.561), # Ga
(0.400,0.561,0.561), # Ge
(0.741,0.502,0.890), # As
(1.000,0.631,0.000), # Se
(0.651,0.161,0.161), # Br
(0.361,0.722,0.820), # Kr
(0.439,0.180,0.690), # Rb
(0.000,1.000,0.000), # Sr
(0.580,1.000,1.000), # Y
(0.580,0.878,0.878), # Zr
(0.451,0.761,0.788), # Nb
(0.329,0.710,0.710), # Mo
(0.231,0.620,0.620), # Tc
(0.141,0.561,0.561), # Ru
(0.039,0.490,0.549), # Rh
(0.000,0.412,0.522), # Pd
(0.753,0.753,0.753), # Ag
(1.000,0.851,0.561), # Cd
(0.651,0.459,0.451), # In
(0.400,0.502,0.502), # Sn
(0.620,0.388,0.710), # Sb
(0.831,0.478,0.000), # Te
(0.580,0.000,0.580), # I
(0.259,0.620,0.690), # Xe
(0.341,0.090,0.561), # Cs
(0.000,0.788,0.000), # Ba
(0.439,0.831,1.000), # La
(1.000,1.000,0.780), # Ce
(0.851,1.000,0.780), # Pr
(0.780,1.000,0.780), # Nd
(0.639,1.000,0.780), # Pm
(0.561,1.000,0.780), # Sm
(0.380,1.000,0.780), # Eu
(0.271,1.000,0.780), # Gd
(0.188,1.000,0.780), # Tb
(0.122,1.000,0.780), # Dy
(0.000,1.000,0.612), # Ho
(0.000,0.902,0.459), # Er
(0.000,0.831,0.322), # Tm
(0.000,0.749,0.220), # Yb
(0.000,0.671,0.141), # Lu
(0.302,0.761,1.000), # Hf
(0.302,0.651,1.000), # Ta
(0.129,0.580,0.839), # W
(0.149,0.490,0.671), # Re
(0.149,0.400,0.588), # Os
(0.090,0.329,0.529), # Ir
(0.816,0.816,0.878), # Pt
(1.000,0.820,0.137), # Au
(0.722,0.722,0.816), # Hg
(0.651,0.329,0.302), # Tl
(0.341,0.349,0.380), # Pb
(0.620,0.310,0.710), # Bi
(0.671,0.361,0.000), # Po
(0.459,0.310,0.271), # At
(0.259,0.510,0.588), # Rn
(0.259,0.000,0.400), # Fr
(0.000,0.490,0.000), # Ra
(0.439,0.671,0.980), # Ac
(0.000,0.729,1.000), # Th
(0.000,0.631,1.000), # Pa
(0.000,0.561,1.000), # U
(0.000,0.502,1.000), # Np
(0.000,0.420,1.000), # Pu
(0.329,0.361,0.949), # Am
(0.471,0.361,0.890), # Cm
(0.541,0.310,0.890), # Bk
(0.631,0.212,0.831), # Cf
(0.702,0.122,0.831), # Es
(0.702,0.122,0.729), # Fm
(0.702,0.051,0.651), # Md
(0.741,0.051,0.529), # No
(0.780,0.000,0.400), # Lr
(0.800,0.000,0.349), # Rf
(0.820,0.000,0.310), # Db
(0.851,0.000,0.271), # Sg
(0.878,0.000,0.220), # Bh
(0.902,0.000,0.180), # Hs
(0.922,0.000,0.149), # Mt
])

# CPK colors in units of RGB values:
cpk_colors = np.array([
(1.000,0.000,0.000) ,# None
(1.000,1.000,1.000) ,# H
(1.000,0.753,0.796) ,# He
(0.698,0.133,0.133) ,# Li
(1.000,0.078,0.576) ,# Be
(0.000,1.000,0.000) ,# B
(0.784,0.784,0.784) ,# C
(0.561,0.561,1.000) ,# N
(0.941,0.000,0.000) ,# O
(0.855,0.647,0.125) ,# F
(1.000,0.078,0.576) ,# Ne
(0.000,0.000,1.000) ,# Na
(0.133,0.545,0.133) ,# Mg
(0.502,0.502,0.565) ,# Al
(0.855,0.647,0.125) ,# Si
(1.000,0.647,0.000) ,# P
(1.000,0.784,0.196) ,# S
(0.000,1.000,0.000) ,# Cl
(1.000,0.078,0.576) ,# Ar
(1.000,0.078,0.576) ,# K
(0.502,0.502,0.565) ,# Ca
(1.000,0.078,0.576) ,# Sc
(0.502,0.502,0.565) ,# Ti
(1.000,0.078,0.576) ,# V
(0.502,0.502,0.565) ,# Cr
(0.502,0.502,0.565) ,# Mn
(1.000,0.647,0.000) ,# Fe
(1.000,0.078,0.576) ,# Co
(0.647,0.165,0.165) ,# Ni
(0.647,0.165,0.165) ,# Cu
(0.647,0.165,0.165) ,# Zn
(1.000,0.078,0.576) ,# Ga
(1.000,0.078,0.576) ,# Ge
(1.000,0.078,0.576) ,# As
(1.000,0.078,0.576) ,# Se
(0.647,0.165,0.165) ,# Br
(1.000,0.078,0.576) ,# Kr
(1.000,0.078,0.576) ,# Rb
(1.000,0.078,0.576) ,# Sr
(1.000,0.078,0.576) ,# Y
(1.000,0.078,0.576) ,# Zr
(1.000,0.078,0.576) ,# Nb
(1.000,0.078,0.576) ,# Mo
(1.000,0.078,0.576) ,# Tc
(1.000,0.078,0.576) ,# Ru
(1.000,0.078,0.576) ,# Rh
(1.000,0.078,0.576) ,# Pd
(0.502,0.502,0.565) ,# Ag
(1.000,0.078,0.576) ,# Cd
(1.000,0.078,0.576) ,# In
(1.000,0.078,0.576) ,# Sn
(1.000,0.078,0.576) ,# Sb
(1.000,0.078,0.576) ,# Te
(0.627,0.125,0.941) ,# I
(1.000,0.078,0.576) ,# Xe
(1.000,0.078,0.576) ,# Cs
(1.000,0.647,0.000) ,# Ba
(1.000,0.078,0.576) ,# La
(1.000,0.078,0.576) ,# Ce
(1.000,0.078,0.576) ,# Pr
(1.000,0.078,0.576) ,# Nd
(1.000,0.078,0.576) ,# Pm
(1.000,0.078,0.576) ,# Sm
(1.000,0.078,0.576) ,# Eu
(1.000,0.078,0.576) ,# Gd
(1.000,0.078,0.576) ,# Tb
(1.000,0.078,0.576) ,# Dy
(1.000,0.078,0.576) ,# Ho
(1.000,0.078,0.576) ,# Er
(1.000,0.078,0.576) ,# Tm
(1.000,0.078,0.576) ,# Yb
(1.000,0.078,0.576) ,# Lu
(1.000,0.078,0.576) ,# Hf
(1.000,0.078,0.576) ,# Ta
(1.000,0.078,0.576) ,# W
(1.000,0.078,0.576) ,# Re
(1.000,0.078,0.576) ,# Os
(1.000,0.078,0.576) ,# Ir
(1.000,0.078,0.576) ,# Pt
(0.855,0.647,0.125) ,# Au
(1.000,0.078,0.576) ,# Hg
(1.000,0.078,0.576) ,# Tl
(1.000,0.078,0.576) ,# Pb
(1.000,0.078,0.576) ,# Bi
(1.000,0.078,0.576) ,# Po
(1.000,0.078,0.576) ,# At
(1.000,1.000,1.000) ,# Rn
(1.000,1.000,1.000) ,# Fr
(1.000,1.000,1.000) ,# Ra
(1.000,1.000,1.000) ,# Ac
(1.000,0.078,0.576) ,# Th
(1.000,1.000,1.000) ,# Pa
(1.000,0.078,0.576) ,# U
(1.000,1.000,1.000) ,# Np
(1.000,1.000,1.000) ,# Pu
(1.000,1.000,1.000) ,# Am
(1.000,1.000,1.000) ,# Cm
(1.000,1.000,1.000) ,# Bk
(1.000,1.000,1.000) ,# Cf
(1.000,1.000,1.000) ,# Es
(1.000,1.000,1.000) ,# Fm
(1.000,1.000,1.000) ,# Md
(1.000,1.000,1.000) ,# No
(1.000,1.000,1.000)  # Lw
])

if __name__ == '__main__':
    from ase.io import read
    atoms = read('/Users/michaeljstatt/tmp/1529386388.3359904_qn.traj')
    pa_obj = PlotlyAtoms(atoms_obj = atoms)
    print(pa_obj.plot())
