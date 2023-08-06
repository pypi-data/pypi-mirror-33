#Typing Imports
import typing as typ

if typ.TYPE_CHECKING:
    from adsorber.objects.asv import AdsorbateSiteVector

#External imports
import pymatgen as pmg                                                       # type: ignore
from pymatgen.io.ase         import AseAtomsAdaptor                           # type: ignore
from pymatgen.core.surface     import SlabGenerator,Slab                        # type: ignore
from pymatgen.analysis.adsorption import AdsorbateSiteFinder                 # type: ignore
from pymatgen.analysis.adsorption import (AdsorbateSiteFinder, reorient_z    # type: ignore
                                         ,patches,color_dict, get_rot, Path) # type: ignore

import numpy as np              # type: ignore
import ase,itertools,os         # type: ignore
import matplotlib               # type: ignore
matplotlib.use('Qt5Agg')        # type: ignore
import matplotlib.pyplot as plt # type: ignore

def flatten(lol : typ.List[list]) -> list:
    return [item for sublist in lol for item in sublist] #flattens a List Of Lists to a list

##############
# Element lists
###############
nonmetal_symbs   = ['H','C','N','P','O','S','Se','F','Cl','Br','I','At','He','Ne','Ar','Kr','Xe','Rn']
nonmetals        = [ase.data.chemical_symbols.index(x) for x in nonmetal_symbs]

def write_asv_list(asv_list      : typ.List["AdsorbateSiteVector"],
                  directory_name : str
                  ) -> None:
    pwd = os.getcwd()
    os.mkdir(os.path.join(pwd,directory_name))
    for asv_obj in asv_list:
        atoms_obj = asv_obj.get_adsorbed_surface()
        ads_str   = asv_obj.ads.name
        site_str  = asv_obj.site.site_type
        vec_str   = '-'.join([str(int(x)) for x in asv_obj.site_vector.round().tolist()])
        dir_name  = '_'.join([ads_str,site_str,vec_str])
        os.mkdir(os.path.join(pwd,directory_name,dir_name))
        ase.io.write(os.path.join(pwd,directory_name,dir_name,'init.traj'),atoms_obj)

#############
# Site Related
###############
def make_pmg_slab(a : ase.Atoms,facet : typ.List[int]) -> pmg.Structure:
    species             = a.get_chemical_symbols()
    coords              = a.get_positions()
    miller_index        = facet
    oriented_unit_cell  = AseAtomsAdaptor.get_structure(a)
    shift               = 0    #???????
    scale_factor        = None #???????
    return Slab(oriented_unit_cell.lattice, species, coords, miller_index,oriented_unit_cell, shift, scale_factor,coords_are_cartesian=True)

def get_sites(a           : ase.Atoms
             ,facet       : typ.List[int]
             ,site_type   : str   = 'all'
             ,symm_reduce : float = 0.0
             ,height      : float = 1.0
             ) -> typ.Any:
    assert site_type in ['all','bridge','ontop','hollow'], 'Please supply a valid site_type'

    slab          = make_pmg_slab(a,facet)
    oriented_slab = reorient_z(slab)
    sites         = AdsorbateSiteFinder(oriented_slab,height = height).find_adsorption_sites(symm_reduce=symm_reduce, distance = 0)[site_type]
    return sites

def show_sites(a             : ase.Atoms
              ,facet        : typ.List[int]
              ,site_type   : str   = 'all'
              ,symm_reduce : float = 0.01
              ,height        : float = 0.9
              )-> typ.Any:
    slab = make_pmg_slab(a,facet)
    plot_slab(slab,plt.gca(),repeat=3,site_type = site_type, symm_reduce=symm_reduce, height = height)
    plt.show() # user looks, closes plot to continue

def get_mic_distance(p1      : np.array
                    ,p2        : np.array
                    ,cell    : np.array
                    ,pbc        : typ.List[int]
                    ,dis_ind : str = 'xyz'
                    ) -> float:
    """ This method calculates the shortest distance between p1 and p2
         through the cell boundaries defined by cell and pbc.
         This method works for reasonable unit cells, but not for extremely
         elongated ones.
    """
    ct = cell.T
    pos = np.mat((p1, p2))
    scaled = np.linalg.solve(ct, pos.T).T
    for i in range(3):
        if pbc[i]:
            scaled[:, i] %= 1.0
            scaled[:, i] %= 1.0
    P = np.dot(scaled, cell)

    pbc_directions = [[-1, 1] * int(direction) + [0] for direction in pbc]
    translations = np.mat(list(itertools.product(*pbc_directions))).T
    p0r = np.tile(np.reshape(P[0, :], (3, 1)), (1, translations.shape[1]))
    p1r = np.tile(np.reshape(P[1, :], (3, 1)), (1, translations.shape[1]))
    dp_vec = p0r + ct * translations
    if dis_ind == 'xyz':
        squared_dis = np.power((p1r - dp_vec), 2).sum(axis=0)
    elif dis_ind =='xy':
        squared_dis = np.power((p1r - dp_vec)[0:2], 2).sum(axis=0)
    else:
        raise ValueError('Please provide valid direction to include in distance \'xy\' or \'xyz\'')
    d = np.min(squared_dis)**0.5
    return d


def plot_slab(slab             : pmg.Structure
             ,ax               : typ.Any
             ,scale            : float               = 0.8
             ,repeat           : int                 = 5
             ,window           : float               = 1.5
             ,draw_unit_cell   : bool                = True
             ,decay            : float               = 0.2
             ,adsorption_sites : bool                = True
             ,site_type        : str                 = 'all'
             ,symm_reduce      : float               = 0.01
             ,atoms_to_draw    : typ.List[ase.Atoms] = []
             ,height           : float               = 0.9
             ) -> typ.Any:
    """Function that helps visualize the slab in a 2-D plot, for
    convenient viewing of output of AdsorbateSiteFinder.

    Args:
        slab (slab): Slab object to be visualized
        ax (axes): matplotlib axes with which to visualize
        scale (float): radius scaling for sites
        repeat (int): number of repeating unit cells to visualize
        window (float): window for setting the axes limits, is essentially
            a fraction of the unit cell limits
        draw_unit_cell (bool): flag indicating whether or not to draw cell
        decay (float): how the alpha-value decays along the z-axis"""

    orig_slab = slab.copy()
    slab      = reorient_z(slab)
    orig_cell = slab.lattice.matrix.copy()
    if repeat:
        slab.make_supercell([repeat, repeat, 1])
    coords    = np.array(sorted(slab.cart_coords, key=lambda x: x[2]))
    sites     = sorted(slab.sites, key=lambda x: x.coords[2])
    alphas    = 1 - decay * (np.max(coords[:, 2]) - coords[:, 2])
    alphas    = alphas.clip(min=0)
    corner    = [0, 0, slab.lattice.get_fractional_coords(coords[-1])[-1]]
    corner    = slab.lattice.get_cartesian_coords(corner)[:2]
    verts     = orig_cell[:2, :2]
    lattsum   = verts[0] + verts[1]

    # Draw circles at sites and stack them accordingly
    for n, coord in enumerate(coords):
        r = sites[n].specie.atomic_radius * scale
        ax.add_patch(patches.Circle(coord[:2] - lattsum * (repeat // 2),
                                    r, color='w', zorder=2 * n))
        color = color_dict[sites[n].species_string]
        ax.add_patch(patches.Circle(coord[:2] - lattsum * (repeat // 2), r,
                                    facecolor=color, alpha=alphas[n],
                                    edgecolor='k', lw=0.3, zorder=2 * n + 1))
    # Adsorption sites
    if adsorption_sites:
        asf = AdsorbateSiteFinder(orig_slab, height=height)
        ads_sites_to_plot = asf.find_adsorption_sites(symm_reduce = symm_reduce)[site_type]
        sop = get_rot(orig_slab)
        ads_sites_to_plot = [sop.operate(ads_site_to_plot)[:2].tolist()
                     for ads_site_to_plot in ads_sites_to_plot]
        ax.plot(*zip(*ads_sites_to_plot), color='k', marker='x',
                markersize=10, mew=1, linestyle='', zorder=10000)

    for atom in atoms_to_draw:
        ax.add_patch(patches.Circle(atom.position[:2]
                    ,ase.data.covalent_radii[atom.number]*scale
                    ,facecolor=color_dict[atom.symbol], alpha=1
                    ,edgecolor='r', lw=1, zorder=10000))

    # Draw unit cell
    if draw_unit_cell:
        verts = np.insert(verts, 1, lattsum, axis=0).tolist()
        verts += [[0., 0.]]
        verts = [[0., 0.]] + verts
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO,
                 Path.LINETO, Path.CLOSEPOLY]
        verts = [(np.array(vert) + corner).tolist() for vert in verts]
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='none', lw=2,
                                  alpha=0.5, zorder=2 * n + 2)
        ax.add_patch(patch)
    ax.set_aspect("equal")
    center = corner + lattsum / 2.
    extent = np.max(lattsum)
    lim_array = [center - extent * window, center + extent * window]
    x_lim = [ele[0] for ele in lim_array]
    y_lim = [ele[1] for ele in lim_array]
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    return ax
