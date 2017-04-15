# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SuddenRasterTools
                                 A QGIS plugin
 This is a tool collection for raster processing
                              -------------------
        begin                : 2017-04-15
        git sha              : $Format:%H$
        copyright            : (C) 2017 by none
        email                : none
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from suddenrastertools_dialog import SuddenRasterToolsDialog
import os.path


class SuddenRasterTools:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SuddenRasterTools_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Sudden Raster Tools')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SuddenRasterTools')
        self.toolbar.setObjectName(u'SuddenRasterTools')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SuddenRasterTools', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = SuddenRasterToolsDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SuddenRasterTools/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Sudden Raster Tools'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Sudden Raster Tools'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def dataset_statistics(self, dataset_path):
        
        from os import path
        from osgeo import gdal
        
        (root, filename) = path.split(dataset_path)
        dataset = gdal.Open(dataset_path)
        band = dataset.GetRasterBand(1)    
        BandType = gdal.GetDataTypeName(band.DataType)
        
        
        text = "# Statistics \n"
        text += "# Filename: %s \n" % filename
        text += "# Location: %s \n" % root        
        text += "# Size: rows = %d, columns = %d \n" % (band.YSize, band.XSize)
        text += "# Data type: %s \n" % BandType
        text += "\n"
        
        return text
            
    def raster_category_variables(self, layer, print_statistics, verbose):
        
        from os import path
        import struct
        from osgeo import gdal
        from qgis.core import *
        from qgis.utils import *
        
        outputtext = ""
        
        layerList = QgsMapLayerRegistry.instance().mapLayersByName(layer)
        if layerList: 
            layer = layerList[0]
        else:
            return
            
        layer = iface.activeLayer()
        provider = layer.dataProvider()

        fmttypes = {'Byte':'B', 'UInt16':'H', 'Int16':'h', 'UInt32':'I', 'Int32':'i', 'Float32':'f', 'Float64':'d'}

        dataset_path = provider.dataSourceUri()
        (root, filename) = path.split(dataset_path)
        dataset = gdal.Open(dataset_path)
        band = dataset.GetRasterBand(1)
        BandType = gdal.GetDataTypeName(band.DataType)
        
        if print_statistics == True:
            outputtext += self.dataset_statistics(dataset_path)

        categories_value = []
        categories_count = []

        for y in range(band.YSize):

            scanline = band.ReadRaster(0, y, band.XSize, 1, band.XSize, 1, band.DataType)
            values = struct.unpack(fmttypes[BandType] * band.XSize, scanline)
            
            for value in values:
                
                #
                # If it is not in the array, add it
                #
                if value not in categories_value:
                    categories_value.append(value)
                    categories_count.append(0)
                
                #
                # Now get the index of the category
                #
                idx = categories_value.index(value)
                
                #
                # Increment the counter for that category
                #
                categories_count[idx] += 1


		total_cells = band.YSize * band.XSize
		
        for i, cat in enumerate(categories_value):
            count_value = cat
            count_cat = categories_count[i]
            count_cat_perc = (float(count_cat) / float(total_cells)) * float(100)
            outputtext +=  "%d > %d | %.2f \n" % (count_value, count_cat, count_cat_perc)

        outputtext +=  "total > %d \n" % (total_cells)
        dataset = None        
        self.dlg.plainTextEdit.appendPlainText(outputtext)
            
            
    def run(self):
        """Run method that performs all the real work"""
        
        #
        # Clear comboBox if the plugin has been used already
        #
        self.dlg.comboBox.clear()
         
        #
        # Select the layers and add them to the dialog
        #
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
             layer_list.append(layer.name())
             self.dlg.comboBox.addItems(layer_list)    
    
        #
        # This is the wrapper that is called on click
        #
        def wrapper():
            #
            # Get currently activated layer
            #
            layer = str(self.dlg.comboBox.currentText())
            print_statistics_checked = self.dlg.print_statistics_checkbox.isChecked() # returns True if checked
            verbose_calculation_checked = self.dlg.verbose_calculation_checkbox.isChecked() # returns True if checked
            self.raster_category_variables(layer, print_statistics_checked, verbose_calculation_checked)
        
        #
        # This is the button that triggers the calculation
        #
        self.dlg.pushButton.clicked.connect(wrapper)
        
        
        #         
        # show the dialog
        #
        self.dlg.show()
        
        #
        # Run the dialog event loop
        #
        result = self.dlg.exec_()
        
        #
        # See if OK was pressed
        #
        if result:
            pass
            

           
