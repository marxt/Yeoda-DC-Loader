# -*- coding: utf-8 -*-
"""
/***************************************************************************
 YeodaDCLoader
                                 A QGIS plugin
 Loads a Yeoda filenamed directory to QGIS, sets time element
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-10-09
        git sha              : $Format:%H$
        copyright            : (C) 2021 by TUW GEO
        email                : mark.tupas@geo.tuwien.ac.at
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QDateTime, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QListWidget, QLineEdit, QDateTimeEdit, QCheckBox, QListWidgetItem, QProgressDialog, QComboBox, QSpinBox
from qgis.gui import QgsFileWidget

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .yeoda_dc_loader_dialog import YeodaDCLoaderDialog
import os.path
import sys

from qgis.core import QgsRasterLayer, QgsProject, QgsRasterLayerTemporalProperties, QgsDateTimeRange
# TUW packages
plugin_dir = os.path.dirname(__file__)
source_packages_dir = os.path.join(plugin_dir, 'source_packages')

try:
    if source_packages_dir not in sys.path:
        sys.path.append(source_packages_dir)

    from geopathfinder.folder_naming import build_smarttree

except:
    import pip
    pip.main(['install', '--target=%s' % source_packages_dir, 'geopathfinder'])
    #pip.main(['install', '--target=%s' % source_packages_dir, 'yeoda'])
    if source_packages_dir not in sys.path:
        sys.path.append(source_packages_dir)

    from geopathfinder.folder_naming import build_smarttree

class YeodaDCLoader:
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
            'YeodaDCLoader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Yeoda Datacube Loader')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None



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
        return QCoreApplication.translate('YeodaDCLoader', message)


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

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/yeoda_dc_loader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Load Yeoda DC'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Yeoda Datacube Loader'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = YeodaDCLoaderDialog()
            self.basepathFW = self.dlg.findChild(QgsFileWidget, 'basepathFW')
            self.listWidget = self.dlg.findChild(QListWidget, 'listWidget')
            self.namingSchemeCB = self.dlg.findChild(QComboBox, 'namingSchemeCB')

            self.select_fileNaming()

            self.namingSchemeCB.currentTextChanged.connect(self.select_fileNaming)

            #loading settings
            self.qmlFW = self.dlg.findChild(QgsFileWidget, 'qmlFW')
            self.overrideTimeCheckB = self.dlg.findChild(QCheckBox, 'overrideTimeCheckB')
            self.timeOverrideCB = self.dlg.findChild(QComboBox, 'timeOverrideCB')
            self.timeOverrideSB = self.dlg.findChild(QSpinBox, 'timeOverrideSB')

            #filters
            self.tileLE = self.dlg.findChild(QLineEdit, 'tileLE')
            self.varNameLE = self.dlg.findChild(QLineEdit, 'varNameLE')
            self.bandLE = self.dlg.findChild(QLineEdit, 'bandLE')
            self.extraLE = self.dlg.findChild(QLineEdit, 'extraLE')

            # to add time filters
            self.startCheckB = self.dlg.findChild(QCheckBox, 'startCheckB')
            self.endCheckB = self.dlg.findChild(QCheckBox, 'endCheckB')
            self.startDateTimeEdit = self.dlg.findChild(QDateTimeEdit, 'startDateTimeEdit')
            self.endDateTimeEdit = self.dlg.findChild(QDateTimeEdit, 'endDateTimeEdit')

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            try:
                root_dirpath = os.path.dirname(str(self.basepathFW.filePath()))
                folder_hierarchy = ["product", "data_version", "subgrid_name", "tile_name"] #assumed
                dir_tree = build_smarttree(root_dirpath, folder_hierarchy, register_file_pattern="^[^Q].*.tif")
                filepaths = dir_tree.file_register
            except OSError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Invalid base path")
                msg.setInformativeText("Please select base path")
                msg.setWindowTitle("Warning")
                msg.exec_()
            else:
                self.filter_dictionary = self.get_filter_dictionary()

                pd = QProgressDialog("Querying files", "Cancel", 0, len(filepaths))
                pd.setWindowModality(Qt.WindowModal)
                count = 0  # a2

                for filepath in filepaths:

                    self.loadRLayer(filepath)

                    count += 1
                    pd.setValue(count)
                    if pd.wasCanceled():
                        pd = None
                        return

    def select_fileNaming(self):
        """sets naming scheme variable and imports smartfile name"""
        self.naming_scheme = str(self.namingSchemeCB.currentText())

        if self.naming_scheme == 'Yeoda':
            from geopathfinder.naming_conventions.yeoda_naming import YeodaFilename
            self.SmartFileName = YeodaFilename
        elif self.naming_scheme == 'ACube':
            from geopathfinder.naming_conventions.acube_naming import ACubeFilename
            self.SmartFileName = ACubeFilename
        elif self.naming_scheme == 'BMon':
            from geopathfinder.naming_conventions.bmon_naming import BMonFilename
            self.SmartFileName = BMonFilename
        elif self.naming_scheme == 'EODR':
            from geopathfinder.naming_conventions.eodr_naming import EODRFilename
            self.SmartFileName = EODRFilename
        elif self.naming_scheme == 'SGRT':
            from geopathfinder.naming_conventions.sgrt_naming import SgrtFilename
            self.SmartFileName = SgrtFilename

        self.listWidget.clear()
        for k in self.SmartFileName.fields_def.keys():
            QListWidgetItem(k, self.listWidget) #populates the list widget

    def get_filter_dictionary(self):
        """creates filter dictionary based on the GUI elements and entries, fields matched based on naing scheme"""
        filter_dictionary = {}
        if self.naming_scheme == 'Yeoda':
            filter_dictionary['tile_name'] = self.tileLE.text().strip()
            filter_dictionary['var_name'] = self.varNameLE.text().strip()
            filter_dictionary['start_time'] = self.startDateTimeEdit.dateTime()
            filter_dictionary['end_time'] = self.endDateTimeEdit.dateTime()
            filter_dictionary['band'] = self.bandLE.text().strip()
            filter_dictionary['extra_field'] = self.extraLE.text().strip()
        elif self.naming_scheme == 'ACube':
            filter_dictionary['tile_name'] = self.tileLE.text().strip()
            filter_dictionary['var_name'] = self.varNameLE.text().strip()
            filter_dictionary['start_time'] = self.startDateTimeEdit.dateTime()
            filter_dictionary['end_time'] = self.endDateTimeEdit.dateTime()
            filter_dictionary['pol'] = self.bandLE.text().strip()
            filter_dictionary['direction'] = self.extraLE.text().strip()
        elif self.naming_scheme == 'BMon': #not tested
            filter_dictionary['var_name'] = self.varNameLE.text().strip()
            filter_dictionary['start_time'] = self.startDateTimeEdit.dateTime()
            filter_dictionary['end_time'] = self.endDateTimeEdit.dateTime()
            filter_dictionary['version'] = self.bandLE.text().strip()
            filter_dictionary['sres'] = self.extraLE.text().strip()
        elif self.naming_scheme == 'SGRT':
            filter_dictionary['tile_name'] = self.tileLE.text().strip()
            filter_dictionary['var_name'] = self.varNameLE.text().strip()
            filter_dictionary['start_time'] = self.startDateTimeEdit.dateTime()
            filter_dictionary['end_time'] = self.endDateTimeEdit.dateTime()
            filter_dictionary['pol'] = self.bandLE.text().strip()
            filter_dictionary['relative_orbit'] = self.extraLE.text().strip()
        elif self.naming_scheme == 'EODR': #not tested
            filter_dictionary['counter'] = self.tileLE.text().strip()
            filter_dictionary['id'] = self.varNameLE.text().strip()
            filter_dictionary['start_time'] = self.startDateTimeEdit.dateTime()
            filter_dictionary['end_time'] = self.endDateTimeEdit.dateTime()
            filter_dictionary['band'] = self.bandLE.text().strip()
            filter_dictionary['file_num'] = self.extraLE.text().strip()
        return filter_dictionary

    def filters(self, file_name, filter_dictionary):
        """checks the filters"""

        allow = True
        dt1 = QDateTime.fromString(str(file_name.stime), 'yyyy-MM-dd hh:mm:ss')

        if file_name.etime is None:
            dt2 = dt1
        else:
            dt2 = QDateTime.fromString(str(file_name.etime), 'yyyy-MM-dd hh:mm:ss')

        for (key, value) in filter_dictionary.items():

            if key == 'start_time' and self.startCheckB.isChecked():
                allow = allow and (filter_dictionary['start_time'] <= dt1)
                    #add check if dt1 is None, catch exception error dialog TODO
            elif key == 'end_time'and  self.endCheckB.isChecked():
                allow = allow and (filter_dictionary['end_time'] >= dt2)
            elif ',' in value: #multiple values, slow but works, to be replaced by prefilters
                values = value.split(',')
                allow_temp = False
                for v in values:
                    if key == 'relative_orbit':
                        allow_temp = allow_temp or v.strip() == "%s%03i" % (file_name['orbit_direction'], file_name[key])
                    else:
                        allow_temp = allow_temp or v.strip() == file_name[key]
                allow = allow and allow_temp
            elif value != '': #none empty string comparison
                if key == 'relative_orbit':
                    allow = allow and (value == "%s%03i" % (file_name['orbit_direction'], file_name[key]))
                else:
                    allow = allow and (value == file_name[key])
            elif value == '': #empty string comparison
                allow = allow and True

        return allow, dt1, dt2

    def loadRLayer(self, path):
        """Loads raster layer if field filters allows, applies temproal properties and style"""

        base_filename = os.path.basename(path)
        filename = self.SmartFileName.from_filename(base_filename, True)
        allow, dt1, dt2 = self.filters(filename, self.filter_dictionary)

        if allow:
            layer_title = ''

            for item in self.listWidget.selectedItems():
                layer_title += "%s " % filename[item.text()]

            if layer_title == '':
                layer_title = base_filename

            rlayer = QgsRasterLayer(path, layer_title)
            if not rlayer.isValid():
                print("Layer %s failed to load!" % (layer_title))
              
            qml_path = str(self.qmlFW.filePath()) #styling should be applied first since, some styles apply temp prop as well
            if qml_path != '':
                rlayer.loadNamedStyle(qml_path)
                rlayer.triggerRepaint()

            QgsProject.instance().addMapLayer(rlayer) #adding layer

            rlayer.temporalProperties().setMode(QgsRasterLayerTemporalProperties.ModeFixedTemporalRange)

            if self.overrideTimeCheckB.isChecked():
                timeInt = str(self.timeOverrideCB.currentText())
                if timeInt == 'days':
                    dt2 = dt1.addDays(int(self.timeOverrideSB.value()))
                elif timeInt == 'hours':
                    dt2 = dt1.addSecs(int(self.timeOverrideSB.value())*3600)
                elif timeInt == 'years':
                    dt2 = dt1.addYears(int(self.timeOverrideSB.value()))
                elif timeInt == 'months':
                    dt2 = dt1.addMonths(int(self.timeOverrideSB.value()))

            if dt1 == dt2:
                dt2 = dt2.addDays(1)

            time_range = QgsDateTimeRange(dt1, dt2)
            rlayer.temporalProperties().setFixedTemporalRange(time_range)
            rlayer.temporalProperties().setIsActive(True)

            

