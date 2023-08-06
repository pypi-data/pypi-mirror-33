# Typing modules
import typing as typ

#External modules
import os,json,time,re
import numpy as np              # type: ignore
import pymatgen as pmg          # type: ignore
from pymatgen.analysis.adsorption import AdsorbateSiteFinder, reorient_z, patches, color_dict, get_rot, Path # type: ignore


"""
Printing and parsing functions


np_to_str
read_on_sher
digit
alpha
alpha_num_split
ask
s
print_sleep
abbreviate_dict
read_storage_json
parse_line
storagedir_to_pckl
print_time
"""
################################################################################

def print_time(floatHours : float) -> str:
    intHours = int(floatHours)
    return "%02d:%02d" % (intHours,(floatHours-intHours)*60)


def read_storage_json(file_path : str) -> str:
    """

    """
    if file_path[0] == '.':
        file_path = os.getcwd()+file_path.replace('.','',1)
    file_text = read_on_sher(file_path)
    return json.loads(file_text)

def parse_line(string : str
              ,substr : str
              ,index  : int =0
              ) -> str:
    """
    Returns the first line containing substring
    """
    return [line for line in string.split('\n') if substr in line][index]


def abbreviate_dict(d : dict)->str:
    strdict =  '\n'.join(['%s : %s'%(k,v if len(str(v))<100 else '...') for k,v in sorted(d.items()) if v is not None])
    nonelist= "\n\n'None' keys: "+','.join(sorted([k for k,v in d.items() if v is None]))
    return strdict+nonelist

def s(x : str) -> str:
    """
    """
    return "'"+str(x)+"'" if isinstance(x,str) else str(x)

def ask(x : str)->typ.Any:
    """
    """
    return input(x+'\n(y/n)---> ').lower() in ['y','yes']

def print_sleep(n : int) -> None:
    """
    """
    for i in reversed(range(n)):
        print("sleeping ...." + (" %d ..."%i if n > 1 else ''))
        time.sleep(1)


def np_to_str(np_obj : np.array
             ,n 	 : int  	= 3
             ,matrix : bool 	= True
             ) -> str:
    """
    The result should be JSON parsable back to a list (or list of lists)
    """
    def rnd(x : float) -> float:
        x = x if abs(x) > 10**(-n) else abs(x)
        return ('{:.%df}'%n).format(x,prec=n) # type: ignore
    if matrix: return str(map(lambda y: map(lambda x: rnd(x),y),np_obj)).replace("'",'')
    else:      return str(map(lambda x: rnd(x),np_obj)).replace("'",'')

def get_sher_pth(pth : str) -> str:
    if   'nfs'    in pth: pth = pth.replace('/nfs/slac/g/suncatfs/ksb/share',  '/scratch/users/ksb/share/suncat_jobs_copy')
    elif 'global' in pth: pth = pth.replace('/global/cscratch1/sd/krisb/share','/scratch/users/ksb/share/nersc_jobs_copy')
    return pth

def read_on_sher(pth : str) -> str:
    """
    Presumes we've rsync'd suncat/share/jobs to sherlock/share/suncat_jobs_copy
    """
    pth_on_sher = get_sher_pth(pth)
    with open(pth_on_sher,'r') as f: return f.read()


def digit(x : str)->str:    return re.sub("[^0-9]","",x)
def alpha(x : str)->str:    return re.sub("[^a-zA-Z]", "", x)
def alpha_num_split(x:str)->typ.Tuple[str,str]:
    return (alpha(x),digit(x))

def roundfloat(x : typ.Any) -> float:
    output =  round(float(x),3)
    return abs(output) if  output == 0 else output





###################
#Archived Scripts
###################
# def folder_name(path : st,updir=0):
#     import os
#     if updir==0:
#         return os.path.basename(path)
#     return os.path.basename(path[0:path.find('/'+folder_name(path, updir-1)[0])])
# def plot_slab(slab 			   : pmg.Structure
#              ,ax 			   : typ.Any
#              ,scale			   : float					= 0.8
#              ,repeat		   : int					= 5
#              ,window		   : float					= 1.5
#              ,draw_unit_cell   : bool   				= True
#              ,decay			   : float  				= 0.2
#              ,adsorption_sites : bool					= True
#              ,site_type 	   : str					= 'all'
#              ,symm_reduce	   : float					= 0.01
#              ,sites_to_draw    : typ.Optional[np.array]	= None
#              ,height 		   : float					= 0.9
#              ) -> typ.Any:
#     """Function that helps visualize the slab in a 2-D plot, for
#     convenient viewing of output of AdsorbateSiteFinder.
#
#     Args:
#         slab (slab): Slab object to be visualized
#         ax (axes): matplotlib axes with which to visualize
#         scale (float): radius scaling for sites
#         repeat (int): number of repeating unit cells to visualize
#         window (float): window for setting the axes limits, is essentially
#             a fraction of the unit cell limits
#         draw_unit_cell (bool): flag indicating whether or not to draw cell
#         decay (float): how the alpha-value decays along the z-axis"""
#
#     orig_slab = slab.copy()
#     # slab = reorient_z(slab)
#     orig_cell = slab.lattice.matrix.copy()
#     if repeat:
#         slab.make_supercell([repeat, repeat, 1])
#     coords = np.array(sorted(slab.cart_coords, key=lambda x: x[2]))
#     sites = sorted(slab.sites, key=lambda x: x.coords[2])
#     alphas = 1 - decay * (np.max(coords[:, 2]) - coords[:, 2])
#     alphas = alphas.clip(min=0)
#     corner = [0, 0, slab.lattice.get_fractional_coords(coords[-1])[-1]]
#     corner = slab.lattice.get_cartesian_coords(corner)[:2]
#     verts = orig_cell[:2, :2]
#     lattsum = verts[0] + verts[1]
#
#     # Draw circles at sites and stack them accordingly
#     for n, coord in enumerate(coords):
#         r = sites[n].specie.atomic_radius * scale
#         ax.add_patch(patches.Circle(coord[:2] - lattsum * (repeat // 2),
#                                     r, color='w', zorder=2 * n))
#         color = color_dict[sites[n].species_string]
#         ax.add_patch(patches.Circle(coord[:2] - lattsum * (repeat // 2), r,
#                                     facecolor=color, alpha=alphas[n],
#                                     edgecolor='k', lw=0.3, zorder=2 * n + 1))
#     # Adsorption sites
#     if adsorption_sites:
#         asf = AdsorbateSiteFinder(orig_slab, height=height)
#         ads_sites_to_plot = asf.find_adsorption_sites(symm_reduce = symm_reduce)[site_type]
#         sop = get_rot(orig_slab)
#         ads_sites_to_plot = [sop.operate(ads_site_to_plot)[:2].tolist()
#                      for ads_site_to_plot in ads_sites_to_plot]
#         ax.plot(*zip(*ads_sites_to_plot), color='k', marker='x',
#                 markersize=10, mew=1, linestyle='', zorder=10000)
#
#     if not sites_to_draw is None:
#         site_xycoords = map(lambda x: x.pos[:2], sites_to_draw)
#         ax.plot(*zip(*site_xycoords), color='k', marker='x',
#                 markersize=10, mew=1, linestyle='', zorder=10000, picker = 5)
#
#     # Draw unit cell
#     if draw_unit_cell:
#         verts = np.insert(verts, 1, lattsum, axis=0).tolist()
#         verts += [[0., 0.]]
#         verts = [[0., 0.]] + verts
#         codes = [Path.MOVETO, Path.LINETO, Path.LINETO,
#                  Path.LINETO, Path.CLOSEPOLY]
#         verts = [(np.array(vert) + corner).tolist() for vert in verts]
#         path = Path(verts, codes)
#         patch = patches.PathPatch(path, facecolor='none', lw=2,
#                                   alpha=0.5, zorder=2 * n + 2)
#         ax.add_patch(patch)
#     ax.set_aspect("equal")
#     center = corner + lattsum / 2.
#     extent = np.max(lattsum)
#     lim_array = [center - extent * window, center + extent * window]
#     x_lim = [ele[0] for ele in lim_array]
#     y_lim = [ele[1] for ele in lim_array]
#     ax.set_xlim(x_lim)
#     ax.set_ylim(y_lim)
#     return ax
