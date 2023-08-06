# Typing modules
import typing as typ

#External Modules
import ase                                      # type: ignore
import numpy as np                              # type: ignore
from ase.neighborlist import NeighborList       # type: ignore
from ase.constraints  import FixedLine          # type: ignore
from ase.data         import covalent_radii     # type: ignore
#Internal Modules
from adsorber.utilities import get_sites


class Site(object):
    def __init__(self
                ,atoms : ase.Atoms
                ,pos   : np.array
                ,facet : typ.List[int]
                )->None:
        self.pos   = pos
        self.atoms = atoms
        self.facet = facet
        self.site_type  = self.kind()


    def kind(self)->str:
        """
        Site -> Site Kind
        (Top/Hollow3/Hollow4/ShortBridge/LongBridge/Step)
        """
        self.neighbors = self.set_neighbors()
        n = len(self.neighbors)
        if   self._check_ontop() and n==1: return "ontop"
        elif n == 2: return "bridge"
        elif n >= 3 or n==1 and not self._check_ontop(): return "hollow"
        else:
            # print('Site has %d neighbors'%n)
            return 'Other'

    def _check_ontop(self
                    ,dx : float = 0.1
                    ) -> bool:
        ontop = False
        if len(self.neighbors) >1:
            neighbor_dis = [np.linalg.norm(self.atoms[neighbor].position[:2]-self.pos[:2]) for neighbor in self.set_neighbors()]
            if np.diff(np.sort(neighbor_dis))[0]>dx and neighbor_dis[0]<0.2:
                ontop = True
        else:
            ontop = True
        return ontop

    def vectors(self) -> typ.List[np.array]:
        """
        Site -> [Vector]
        Initial Orientations we want to attempt for adsorbates
        """
        right_angles  = np.eye(3)
        return list(right_angles)+list(-right_angles)

    def other_sites(self
                   ,site_type : str = 'all'
                   ) -> typ.List["Site"]:
        """
        All sites (no symmetry reduce) for the surface
        """
        sites = get_sites(self.atoms,self.facet,site_type=site_type,symm_reduce=0.0)
        return [Site(self.atoms,p,self.facet) for p in sites]



    def set_neighbors(self)->typ.List[int]:
        """
        Site -> [Atom IDs]
        IDs of atoms in the first step of the radial distribution function
        'Step' dictated by having same # of neighbors with 0.3 A range
        """
        n_neighbors = []

        get_radius = np.vectorize(covalent_radii.__getitem__)

        for dx in np.arange(0,5,0.05): #steps of 0.05 A
            a = self.atoms.copy()

            a.append(ase.Atom('H',self.pos))
            n = NeighborList(dx + get_radius(a.get_atomic_numbers())
                             ,skin=0,self_interaction=False,bothways=True)
            n.update(a)
            n_neighbors.append(len(n.get_neighbors(-1)[0]))

            if n_neighbors[-1]>0:                                     # we're not in startup
                if all(x == n_neighbors[-1] for x in n_neighbors[-2:]): # + last 3 must be equal
                    return n.get_neighbors(-1)[0]
            else:
                return []
        return []

    def _neighbor_vecs(self)->typ.List[np.array]:
        """Turns indices into vectors from site to atom"""
        return [self.atoms[a].position - self.pos for a in self.neighbors]

    def get_neighbor_chemical_symbols(self)->typ.List[str]:
        return list(set(self.atoms[self.neighbors].get_chemical_symbols()))
