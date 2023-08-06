# Typing modules
import typing as typ

if typ.TYPE_CHECKING:
    from adsorber.objects.adsorbate import Adsorbate
    from adsorber.objects.site      import Site

# External Modules
import json
import numpy as np                        # type: ignore
import ase                                # type: ignore
from ase.neighborlist import NeighborList # type: ignore
from ase.constraints import FixedLine     # type: ignore
from ase.data import covalent_radii       # type: ignore

# Internal Modules
from adsorber.utilities       import get_sites, make_pmg_slab, get_mic_distance, plot_slab


################################################################################

class AdsorbateSiteVector(object):
    def __init__(self
                ,ads                : "Adsorbate"
                ,site               : "Site"
                ,vector             : np.array
                ,constraint_dict    : dict               = {}
                ,additional_ads     : typ.List[ase.Atom] = []
                ) -> None:
        """
        A combination of a site object, adsorbate object, and orientation vectors

        Input:
        ads :: Adsorbate Object
        site :: Site object
        vector :: vector
        """
        import numpy as np

        self.ads             = ads #Adsorbate object
        self.site            = site #Site object
        self.site_vector     = vector/np.linalg.norm(vector) #Unit vector
        self.bare            = self.site.atoms.copy() #Bare Surface Ase Atoms Object
        self.constraint_dict = constraint_dict #Constraint Dict for Adsorbate
        self.additional_ads  = additional_ads

    def get_adsorbed_surface(self
                            ,vec             : typ.Optional[np.array] = None
                            ) -> ase.Atoms:
        if vec is None: vec = self.site_vector
        atoms = self.bare.copy()
        for atom in self.additional_ads:
            atoms += atom
        rotated = self._rotate(vec)
        ads_atoms_at_optimal_height = self._place_at_optimal_height(rotated)

        #Append adsorbate atoms while also adding in any adosrbate constraints
        for atom in ads_atoms_at_optimal_height:
            atoms += atom
            atoms.set_constraint(atoms.constraints+self._constrain_ads(atoms[len(atoms)-1]))
        atoms.wrap()
        return atoms

    def _constrain_ads(self
                      ,atom : ase.Atom
                      ) -> list:
        if not self.constraint_dict in [{},None] and self.constraint_dict['mask'](atom):
            if self.constraint_dict['type'].__name__ in ['FixedLine','FixedPlane']:
                return [self.constraint_dict['type'](a = atom.index, **self.constraint_dict['input'])]
            elif self.constraint_dict['type'].__name__ in ['FixAtoms']:
                return [self.constraint_dict['type'](indices = [atom.index])]
            else:
                raise NotImplementedError
        else:
            return []

    def _rotate(self,vec : np.array) -> ase.Atoms:
        """Adsorbate -> Vec -> Atoms"""
        def perpendicular_vector(v : np.array) -> np.array:
            return np.array([1, 1, -1.0 * (v[0] + v[1]) / v[2]])
        modified_atoms = self.ads.atoms.copy()
        axis    = np.cross(self.ads.vector,vec)
        theta   = np.arccos(np.dot(self.ads.vector,vec))
        if theta < 0.01:
            return modified_atoms
        elif round(theta,4) == round(np.pi,4):
            axis = perpendicular_vector(self.site_vector)
        modified_atoms.rotate(a = theta*180/np.pi, v= axis, center = 'COM')
        return modified_atoms

    def _place_at_optimal_height(self
                                ,ads_atoms : ase.Atoms
                                ,dx : float = 0.0
                                ) -> ase.Atoms:

        def rad(atom : ase.Atom) -> float:
            """Get the visual radius of ase.gui"""
            return covalent_radii[atom.number]/1.124

        def near(position    : np.array
                ,dist        : float = 6
                ) -> bool:
            """determine if atom is nearby the position"""
            return get_mic_distance(self.site.pos,position,self.bare.cell, self.bare.pbc) < dist

        def collision(atom1 : ase.Atom
                     ,atom2 : ase.Atom
                     ) -> bool:
            """Check for collision between two atoms (i.e. overlapping spheres in ase gui)"""
            return get_mic_distance(atom1.position,atom2.position, self.bare.cell, self.bare.pbc)<=rad(atom1)+rad(atom2)+dx

        mod_ads_atoms = ads_atoms.copy()
        mod_ads_atoms.positions += self.site.pos
        passed_collision_test = False
        while not passed_collision_test:
            tests = []
            for ads_atom in mod_ads_atoms:
                collision_test_result = all([not collision(atom,ads_atom) for atom in self.bare if near(ads_atom.position,dist = 6)])
                tests.append(collision_test_result)
            if all(tests):
                passed_collision_test = True
            mod_ads_atoms.positions += np.array([0,0,0.1])
        return mod_ads_atoms


#CataLog specific stuff
    def adsorbate_column_entry(self) -> str:
        n = len(self.bare)
        return json.dumps([list(range(n,n+len(self.ads.atoms)))])

    def job_name(self
                ,bare_job_name : str
                ) -> str:
        vec_name = '.'.join(self.site_vector.astype(int).astype(str))
        if self.constraint_dict in [None,{}]:
            constraint_name = 'nocons'
        else:
            constraint_name = self.constraint_dict.get('type').__name__         # type: ignore
        return '_'.join([bare_job_name , self.ads.name, self.site.kind(), constraint_name, vec_name])

    def get_modified_param_dict(self
                               ,param_dict      : dict
                               ) -> dict:
        from catalog.misc.atoms import traj_to_json
        modified_dict                   = param_dict.copy()
        modified_dict['inittraj']       = traj_to_json(self.get_adsorbed_surface())
        modified_dict['job_name']       = self.job_name(modified_dict['job_name'])
        modified_dict['adsorbates']     = self.adsorbate_column_entry()
        return modified_dict
