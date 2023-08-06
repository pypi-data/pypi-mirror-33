# Typing Modules
import typing as typ

if typ.TYPE_CHECKING:
    from adsorber.objects.asv import AdsorbateSiteVector

#External Imports
import inspect, sys
import numpy as np                                                                       # type: ignore
from copy import deepcopy

#-Matplotlib imports
import matplotlib                                                                        # type: ignore
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt                                                          # type: ignore
from matplotlib.figure import Figure                                                     # type: ignore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas               # type: ignore
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar # type: ignore
from matplotlib.lines import Line2D                                                      # type: ignore
from PyQt5 import QtGui, QtWidgets, QtCore                                               # type: ignore
from ase.visualize import view                                                           # type: ignore

#Internal Imports
from adsorber.gui.layout import Ui_MainWindow
from adsorber.utilities  import make_pmg_slab, plot_slab, reorient_z



class MplCanvas(Canvas):
    def __init__(self,
                parent : typ.Any = None
                ) -> None:
        super(MplCanvas, self).__init__(Figure())
        self.setParent(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()

class GUI(QtWidgets.QMainWindow):
    def __init__(self
                ,parent     : typ.Any   = None
                ) -> None:
        #Initialize GUI Layout
        QtWidgets.QWidget.__init__(self, parent)
        self.resize(1000,800)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._build_filter_list()

        #Set up MPL Canvas
        self.ui.canvas = MplCanvas()
        typ.cast(MplCanvas,self.ui.canvas)
        self.figure = self.ui.canvas.figure                         # type: ignore
        self.toolbar = NavigationToolbar(self.ui.canvas,self)
        self.ui.verticalLayout.addWidget(self.toolbar)
        self.ui.verticalLayout.addWidget(self.ui.canvas)

        self.starting_num_asvs = None # type: typ.Optional[int]
        self.asv_list_history  = [] # type: list
        self.plot_ads          = True
        self.set_message('Howdy!')
        #Connect push button/onpick functions
        self.ui.canvas.mpl_connect('pick_event',self._onpick)       # type: ignore
        self.ui.push_select_all.clicked.connect(self._select_all)
        self.ui.push_clear.clicked.connect(self._clear)
        self.ui.push_view.clicked.connect(self._view)
        self.ui.push_quit.clicked.connect(self._quit)
        self.ui.push_finish.clicked.connect(self._finish)
        self.ui.push_apply.clicked.connect(self._apply_filter)
        self.ui.push_undo.clicked.connect(self._undo)
        # self.ui.push_toggle_ads.clicked.connect(self._toggle_ads)
        self.showMaximized()

    ####################################
    #Methods to determine selected sites
    #-----------------------------------

    def _store_sites(self) -> None:
        asv                        = deepcopy(self.asv_list[0])
        self.slab                  = make_pmg_slab(asv.bare,asv.site.facet)
        self.slab                  = reorient_z(self.slab)
        self.additional_ads        = asv.additional_ads
        self.additional_ads_coords = [atom.position for atom in self.additional_ads]
        site_coords                = list(map(lambda x: x.site.pos[:2], self.asv_list)) # type: ignore
        self.site_coords           = list(set([tuple(p) for p in site_coords]))
        self.selected_sited_coords = [[-100.,-100.],[-100.,-100.]]

        #Cast self.site_coords as a list
        typ.cast(list, self.site_coords)

    def plot(self
            ,asv_list       : typ.List["AdsorbateSiteVector"]
            ,axes_limits    : typ.Optional[tuple]            = None
            ) -> None:

        #Set asv data and store sites
        self.asv_list = asv_list
        if len(asv_list)>0:
            self._store_sites()
        else:
            self.site_coords        = [[-100.,-100.],[-100.,-100.]]             # type: ignore

        self.figure.add_axes()
        self.ax = self.figure.gca()

        if self.plot_ads:
            plot_slab(self.slab,self.ax,repeat=3,site_type = 'all', symm_reduce=0.0,adsorption_sites = False,window=1,atoms_to_draw = self.additional_ads)
        else:
            plot_slab(self.slab,self.ax,repeat=3,site_type = 'all', symm_reduce=0.0,adsorption_sites = False,window=1)

        self.ax.set_title('Left click on X\'s to select sites \n Right click on O\'s to deselect sites')

        self.dummy_points           = [[-100.,-100.],[-100.,-100.]]
        #Plot all sites in asv_list
        self.site_plot = self.ax.plot(*zip(*(self.site_coords+self.dummy_points)), color='k', marker='x',markersize = 10, linestyle = '', zorder=10000, picker = 5, label = 'unselected')[0]

        #Make a dummy plot for the selected sites
        selected_sited_coords = self.dummy_points + self.selected_sited_coords
        self.site_selected_plot = self.ax.plot(*selected_sited_coords,color='r', marker='o',markersize = 10,linestyle = '', zorder=10000, picker = 5, label = 'selected')[0]

        if not axes_limits == None:
            self.ax.set_xlim(axes_limits[0]);   # type: ignore
            self.ax.set_ylim(axes_limits[1]);   # type: ignore

        self.redraw_plots()
        self.update_progress(self.asv_list)
        self.ui.canvas.start_event_loop_default()

    ####################################
    #Methods to determine selected sites
    #-----------------------------------

    def _any_selected(self) -> bool:
        return len(self._get_selected_asvs()) > 0


    def _get_selected_asvs(self) -> typ.List["AdsorbateSiteVector"]:
        selected_sited_coords = list(zip(*self.site_selected_plot.get_data()))
        selected_sited_coords = list(filter(lambda xy: xy != (-100,-100),selected_sited_coords))
        selected_asvs = list(filter(lambda asv: tuple(asv.site.pos[0:2]) in selected_sited_coords, self.asv_list))
        return selected_asvs

    ####################################
    #Methods for applying filters
    #-----------------------------------

    def _build_filter_list(self) -> None:
        from adsorber.filter_functions import filter_funcs
        self.filter_list = []   # type: list
        for i,(filter_name,filter_func)  in enumerate(filter_funcs.items()):
            self.filter_list.append(filter_func)
            self.ui.filter_list.addItem("")
            self.ui.filter_list.setItemText(i,QtWidgets.QApplication.translate("MainWindow", filter_name))

    def _apply_filter(self) -> None:
        if not self._any_selected():
            self.set_message('Please select sites to apply filter to')
        else:
            ind = self.ui.filter_list.currentIndex()
            filter_name = self.ui.filter_list.currentText()
            filter_func = self.filter_list[ind]
            old_axes_limits = (self.ax.get_xlim(),self.ax.get_ylim())
            asv_list = self._get_selected_asvs()
            self.asv_list_history.append(asv_list)

            dialogbox = QtWidgets.QInputDialog()
            args = inspect.getfullargspec(filter_func).args
            def_args = self.get_default_args(filter_func)
            html_style  ='<html style="font-size:15pt;">'
            html_footer ='</html>'
            inputs = {}
            for arg in inspect.getfullargspec(filter_func).args:
                default = def_args.get(arg)
                if filter_name == 'site_type_filter':
                    items = ['ontop','bridge','hollow']
                    item, ok = dialogbox.getItem(self, filter_name,'{}Select {}:{}'.format(html_style,arg,html_footer),items,0,False)
                    if item and ok:
                        inputs[arg] = item
                elif isinstance(default,bool):
                    items = ['True','False']
                    item, ok = dialogbox.getItem(self, filter_name,'{}Select {}:{}'.format(html_style,arg,html_footer),items,0,False)
                    if item and ok:
                        inputs[arg] = item == 'True'
                elif isinstance(default,int) or isinstance(default,float):
                    val, ok = dialogbox.getDouble(self, filter_name,'{}Input {}:'.format(html_style,arg,html_footer),default)
                    if val and ok:
                        inputs[arg] = val
                elif isinstance(default,str):
                    val, ok = dialogbox.getText(self, filter_name,'{}Input {} (default is {}):{}'.format(html_style,arg,default,html_footer))
                    if val and ok:
                        inputs[arg] = val
                else:
                    raise NotImplementedError
            filtered_asv_list = filter_func(**inputs)(asv_list)
            message = '{0} filtered out {1} of {2} jobs'.format(filter_name,len(asv_list)-len(filtered_asv_list),len(asv_list))
            self.set_message(message)
            self.figure.clear()
            self.update_progress(filtered_asv_list)
            self.plot(filtered_asv_list, old_axes_limits)

    @staticmethod
    def get_default_args(func : typ.Any) -> dict:
        """
        returns a dictionary of arg_name:default_values for the input function
        """
        argspec          = inspect.getfullargspec(func)
        func_args        = argspec.args
        func_defaults    = argspec.defaults
        if func_args == []:
            return {}
        return dict(zip(func_args[-len(func_defaults):], func_defaults))

    ####################################
    #Methods for push buttons
    #-----------------------------------
    def _select_all(self, event : typ.Any) -> None:
        """
        Selects all sites
        """
        self.site_selected_plot.set_data(*list(zip(*(self.site_coords+self.dummy_points)))) # type: ignore
        self.site_plot.set_data(*self.dummy_points)
        self.redraw_plots()

    def _clear(self, event : typ.Any) -> None:
        """
        Clears all selected sites
        """
        # self = self.filter
        self.site_plot.set_data(*list(zip(*(self.site_coords+self.dummy_points))))
        self.site_selected_plot.set_data(*self.dummy_points)
        self.redraw_plots()

    def _toggle_ads(self, event : typ.Any) -> None:
        """
        Toggles showing the adsorbates
        """
        self.plot_ads = not self.plot_ads
        self.plot(self._get_selected_asvs())

    def _view(self, event : typ.Any) -> None:
        """
        View the currently selected sites in ase-gui
        """
        selected_asvs = self._get_selected_asvs()
        atoms_to_view = [asv_obj.get_adsorbed_surface() for asv_obj in selected_asvs]
        view(atoms_to_view)

    def _quit(self, event : typ.Any) -> None:
        """
        Halts the program
        """
        reply = check_with_user('Are you sure you want to quit?')
        if reply:
            self.ui.canvas.stop_event_loop_default()
            sys.exit()

    def _undo(self, event : typ.Any) -> None:
        if len(self.asv_list_history) == 0:
            self.set_message('No filters to undo')
        else:
            old_axes_limits = (self.ax.get_xlim(),self.ax.get_ylim())
            self.figure.clear()
            self.plot(self.asv_list_history.pop(),old_axes_limits)

    def _finish(self, event : typ.Any) -> None:
        if not self._any_selected():
            quit_msg = 'Are you sure you want to filter all sites?'
            reply = QtWidgets.QMessageBox.question(self, 'Message',
                         quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                return
        self.ui.canvas.stop_event_loop_default()

    ####################################
    #Methods for selecting sites
    #-----------------------------------
    def _onpick(self, event : typ.Any) -> None:

        # self = self.filter
        if isinstance(event.artist, Line2D):
            #Gather data on the event
            ind = event.ind[0]
            thisline = event.artist
            label = thisline.get_label()
            button = event.mouseevent.button
            #Get current values in the two data sets
            selected_sited_coords = list(zip(*self.site_selected_plot.get_data()))
            site_coords = list(zip(*self.site_plot.get_data()))
            #Check if the unselected sites were picked
            if label == 'unselected' and button == 1:
                #Get data of selected point
                point = site_coords[ind]
                #Remove that point from the unselected plot
                site_coords = list(filter(lambda xy: xy != point, site_coords))
                #Add it to the selected plot
                selected_sited_coords.append(point)
                #Set new data
                self.site_selected_plot.set_data(zip(*selected_sited_coords))
                self.site_plot.set_data(zip(*site_coords))
            #Check if a selected site was picked while Ctrl was held down
            elif label == 'selected' and button == 3:
                    #Get data of selected point
                    point = selected_sited_coords[ind]
                    #Remove point from selected sites
                    selected_sited_coords = list(filter(lambda xy: xy != point, selected_sited_coords))
                    #Add the point to the unselected sites
                    site_coords.append(point)
                    #Set new data
                    self.site_plot.set_data(zip(*site_coords))
                    self.site_selected_plot.set_data(zip(*selected_sited_coords))
            #Redraw Plot
            self.redraw_plots()

    ####################################
    #Miscellaneous methods
    #-----------------------------------
    def redraw_plots(self) -> None:
        self.ui.canvas.draw()

    def update_progress(self, asv_list : typ.List["AdsorbateSiteVector"]) -> None:
        if self.starting_num_asvs is None:
            self.starting_num_asvs = int(len(asv_list))
            typ.cast(int, self.starting_num_asvs)
        percent_filtered = 1-float(len(asv_list))/float(self.starting_num_asvs)
        self.ui.num_outputs.setText('Number of Output Structures Remaining: {}/{}'.format(len(asv_list),int(self.starting_num_asvs)))
        self.ui.filter_progress.setValue(percent_filtered*100)

    def set_message(self, text : str) -> None:
        self.ui.messages.setText(text)

def check_with_user(message : str) -> bool:
    quit_msg = 'Are you sure you want to quit?'
    reply = QtWidgets.QMessageBox.question(None, 'Message',
                 quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
    if reply == QtWidgets.QMessageBox.Yes:
        return True
    else:
        return False
