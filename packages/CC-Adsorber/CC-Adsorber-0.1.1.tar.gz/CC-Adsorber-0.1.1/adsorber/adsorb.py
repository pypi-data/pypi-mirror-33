# Typing Modules
import typing as typ

if typ.TYPE_CHECKING:
    pass

#External Imports
import argparse, itertools, os
import ase              # type: ignore
#Internal Imports
import adsorber.filter_functions    as ff
import adsorber.objects.adsorbate   as ads
from adsorber.objects.site          import Site
from adsorber.objects.asv           import AdsorbateSiteVector
import adsorber.utilities           as util


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--traj_file','-t', type =str,help="ASE Traj file of bare slab to adsorb to")
    parser.add_argument('--ads','-a',type =str, help="Space seperated list of adsorbates (i.e. \"H NH\")")


    args = parser.parse_args()

    ########
    #ADHOC WARNING!!!
    facet = [0,0,1]
    #Don't think facet really matters for site AdsorbateSiteFinder so I just use fake facet
    ########

    #Make Site Objects
    bare_slab = ase.io.read(args.traj_file)
    site_positions = util.get_sites(bare_slab,facet = [0,1,0],symm_reduce = 0.,site_type = 'ontop')
    site_list  = [Site(bare_slab.copy(),s_pos,facet) for s_pos in site_positions]

    #Make Adsorbate Objects
    ads_list   = [ads.get_ads(ads_str) for ads_str in args.ads.split()]

    #Make all combinations of Adsorbates, Sites, and Vectors
    ads_site_pairs = itertools.product(ads_list,site_list)
    asv_list = util.flatten([[AdsorbateSiteVector(a,s,v) for v in s.vectors()] for a,s in ads_site_pairs])

    #Default is to simply apply the manual_filter
    new_asv_list = ff.manual_filter()(asv_list)

    util.write_asv_list(new_asv_list, bare_slab.get_chemical_formula())
if __name__ == '__main__':
    main()
