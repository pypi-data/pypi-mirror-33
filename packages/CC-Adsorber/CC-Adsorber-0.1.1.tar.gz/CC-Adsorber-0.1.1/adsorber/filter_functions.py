# Typing Modules
import typing as typ

if typ.TYPE_CHECKING:
    # Type Checking Imports
    from adsorber.objects.asv import AdsorbateSiteVector    # type: ignore
    # Type Aliases
    filter_func_type = typ.Callable[[
        typ.List[AdsorbateSiteVector]], typ.List[AdsorbateSiteVector]]

# External Modules
import numpy as np
import sys
from PyQt5 import QtWidgets             # type: ignore

# Internal Modules
from adsorber.gui import gui

################################################################################


def manual_filter(parent : typ.Any  = None) -> "filter_func_type":
    def filter_func(asv_list: typ.List['AdsorbateSiteVector']
                    ) -> typ.List['AdsorbateSiteVector']:
        import sys
        # Check length of asv_list and that each asv object has same bare surface
        if len(asv_list) == 0:
            filtered_asv_list = asv_list
            print('\tmanual_filter filtered out {0} of {1} jobs'.format(
                len(asv_list) - len(filtered_asv_list), len(asv_list)))
            return filtered_asv_list

        assert all(map(lambda asv: asv.bare == asv_list[0].bare, asv_list)), \
            'asv_list must only include asv objects with identical bare surfaces'

        slabs = list(map(lambda x: x.bare, asv_list))
        assert slabs.count(slabs[0]) == len(
            slabs), 'asv_list must contain only asv objects with the same asv.bare'
        app = None
        if not  QtWidgets.QApplication.instance():
            print('new app')
            app = QtWidgets.QApplication(sys.argv)
        gui_obj = gui.GUI(parent = parent)
        gui_obj.plot(asv_list)
        gui_obj.close()
        if not gui_obj._any_selected() \
                and gui.check_with_user('Do you want to halt program?'):
            print('Manual Site Filter halted by user')
            sys.exit()
            app.deleteLater()
        filtered_asv_list = gui_obj._get_selected_asvs()
        print('\tmanual_filter filtered out {0} of {1} jobs'.format(
            len(asv_list) - len(filtered_asv_list), len(asv_list)))
        return filtered_asv_list

    return filter_func


def symm_filter(symm_reduce: float =0.05
                ) -> "filter_func_type":
    """
    Reduces the set of adsorbate sites by finding removing
    symmetrically equivalent duplicates
    """
    def filter_func(asv_list: typ.List['AdsorbateSiteVector']
                    ) -> typ.List['AdsorbateSiteVector']:
        from pymatgen.symmetry.analyzer import SpacegroupAnalyzer               # type: ignore
        from pymatgen.symmetry.analyzer import generate_full_symmops            # type: ignore
        from pymatgen.util.coord import in_coord_list, in_coord_list_pbc        # type: ignore
        from adsorber.utilities import make_pmg_slab

        if len(asv_list) == 0:
            filtered_asv_list = asv_list
            print('\tmanual_filter filtered out {0} of {1} jobs'.format(
                len(asv_list) - len(filtered_asv_list), len(asv_list)))
            return filtered_asv_list

        slab = make_pmg_slab(asv_list[0].bare, asv_list[0].site.facet)
        surf_sg = SpacegroupAnalyzer(slab, 0.1)
        symm_ops = surf_sg.get_symmetry_operations()
        unique_coords = []  # type: list
        # Convert to fractional
        coords_set = [np.array(site_curr.pos) for site_curr in list(
            map(lambda asv: asv.site, asv_list))]
        coords_set = [slab.lattice.get_fractional_coords(coords)
                      for coords in coords_set]
        for coords in coords_set:
            incoord = False
            for op in symm_ops:
                if in_coord_list_pbc(unique_coords, op.operate(coords),
                                     atol=symm_reduce):
                    incoord = True
                    break
            if not incoord:
                unique_coords += [coords]
        # convert back to cartesian
        reduced_cart_coords = [slab.lattice.get_cartesian_coords(coords)
                               for coords in unique_coords]
        filtered_asv_list = list(filter(lambda asv: in_coord_list(
            reduced_cart_coords, asv.site.pos, atol=symm_reduce), asv_list))
        print('\tsymm_filter filtered out {0} of {1} jobs'.format(
            len(asv_list) - len(filtered_asv_list), len(asv_list)))
        return filtered_asv_list
    return filter_func


def has_neighbor_symbol_filter(ads_name: str = 'metal', return_true_if_symbol_is_neighbor: bool = True
                               ) -> "filter_func_type":
    def filter_func(asv_list: typ.List['AdsorbateSiteVector']
                    ) -> typ.List['AdsorbateSiteVector']:
        def f(asv: 'AdsorbateSiteVector') -> bool:
            from adsorber.utilities import nonmetals
            from ase.data import chemical_symbols           # type: ignore
            nonmetals = list(
                map(lambda A_num: chemical_symbols[A_num], nonmetals))

            if ads_name == 'metal':
                result = any(
                    [symb not in nonmetals for symb in asv.site.get_neighbor_chemical_symbols()])
            elif ads_name == 'nonmetal':
                result = any(
                    [symb in nonmetals for symb in asv.site.get_neighbor_chemical_symbols()])
            else:
                result = ads_name in asv.site.get_neighbor_chemical_symbols()
            if not return_true_if_symbol_is_neighbor:
                result = not result
            return result

        if len(asv_list) == 0:
            filtered_asv_list = asv_list
            print('\tmanual_filter filtered out {0} of {1} jobs'.format(
                len(asv_list) - len(filtered_asv_list), len(asv_list)))
            return filtered_asv_list

        filtered_asv_list = list(filter(f, asv_list))
        print('\thas_neighbor_symbol filtered out {0} of {1} jobs'.format(
            len(asv_list) - len(filtered_asv_list), len(asv_list)))
        return filtered_asv_list
    return filter_func


def positive_vectors_filter() -> "filter_func_type":
    """ Helpful Doc String"""
    def filter_func(asv_list: typ.List['AdsorbateSiteVector']
                    ) -> typ.List['AdsorbateSiteVector']:
        if len(asv_list) == 0:
            filtered_asv_list = asv_list
            print('\tmanual_filter filtered out {0} of {1} jobs'.format(
                len(asv_list) - len(filtered_asv_list), len(asv_list)))
            return filtered_asv_list

        filtered_asv_list = list(filter(lambda asv: all(
            np.array(asv.site_vector) >= 0), asv_list))
        print('\tpositive_vectors filtered out {0} of {1} jobs'.format(
            len(asv_list) - len(filtered_asv_list), len(asv_list)))
        return filtered_asv_list
    return filter_func


def site_type_filter(site_type: str ='ontop'
                     ) -> "filter_func_type":
    """ Helpful Doc String"""
    def filter_func(asv_list: typ.List['AdsorbateSiteVector']
                    ) -> typ.List['AdsorbateSiteVector']:
        if len(asv_list) == 0:
            filtered_asv_list = asv_list
            print('\tmanual_filter filtered out {0} of {1} jobs'.format(
                len(asv_list) - len(filtered_asv_list), len(asv_list)))
            return filtered_asv_list
        filtered_asv_list = list(filter(lambda asv: asv.site.site_type == site_type or asv.site.site_type in site_type, asv_list))
        print('\tsite_type_filter filtered out {0} of {1} jobs'.format(
            len(asv_list) - len(filtered_asv_list), len(asv_list)))
        return filtered_asv_list
    return filter_func


def emt_filter(emttol: float = 0.01
               ) -> "filter_func_type":
    """ Helpful Doc String"""
    def filter_func(asv_list: typ.List['AdsorbateSiteVector']
                    ) -> typ.List['AdsorbateSiteVector']:
        import adsorber.emt as emt # type: ignore

        if len(asv_list) == 0:
            filtered_asv_list = asv_list
            print('\tmanual_filter filtered out {0} of {1} jobs'.format(
                len(asv_list) - len(filtered_asv_list), len(asv_list)))
            return filtered_asv_list

        def get_emt_energy(asv_object: 'AdsorbateSiteVector') -> typ.Tuple[float, 'AdsorbateSiteVector']:
            atoms = asv_object.get_adsorbed_surface()
            atoms.set_calculator(emt.EMT())
            return (atoms.get_potential_energy(), asv_object)
        n = len(asv_list)
        current_emt = -float('inf')
        filtered_asv_list = []
        for eng, dic in sorted(map(get_emt_energy, asv_list), key=lambda x: x[0]):
            if eng - emttol > current_emt:  # we found a distinct inittraj_pckl
                filtered_asv_list.append(dic)
                current_emt = eng
        print('\temt_filter filtered out {0} of {1} jobs'.format(
            len(asv_list) - len(filtered_asv_list), len(asv_list)))
        return filtered_asv_list
    return filter_func


filter_funcs = {
    'symm_filter': symm_filter, 'has_neighbor_symbol_filter': has_neighbor_symbol_filter, 'positive_vectors_filter': positive_vectors_filter, 'site_type_filter': site_type_filter, 'emt_filter': emt_filter
}


def get_filters_funcs(filter_name: str) -> typ.Any:
    return filter_funcs[filter_name]


# def nearest_sites_filter(pos=None,dist = 2,rank = None):
#     def filter_func(asv_list):
#         import numpy as np
#         from CataLog.misc.atoms import get_mic_distance
#
#         if len(asv_list) == 0:
#             filtered_asv_list = asv_list
#             print('\tmanual_filter filtered out {0} of {1} jobs'.format(len(asv_list)-len(filtered_asv_list),len(asv_list)))
#             return filtered_asv_list
#
#         if rank is None:
#             def f(asv):
#                 return get_mic_distance(pos,asv.site.pos,asv.bare.cell, asv.bare.pbc, dis_ind = 'xy') < dist
#             filtered_asv_list = filter(f, asv_list)
#         else:
#             other_sites = site.other_sites(site_type = site_type)
#             site_ind = np.argmin(map(lambda other_site: get_mic_distance(site.pos, other_site.pos,site.atoms.cell, site.atoms.pbc,dis_ind = 'xy'), other_sites))
#             diff = map(lambda site:np.linalg.norm((site.pos-pos)[0:2]), other_sites)
#             print(np.argsort(diff).tolist().index(site_ind) <= rank-1)
#             return np.argsort(diff).tolist().index(site_ind) <= rank-1
#         print('\tnearest_sites filtered out {0} of {1} jobs'.format(len(asv_list)-len(filtered_asv_list),len(asv_list)))
#         return filtered_asv_list
#     return filter_func
