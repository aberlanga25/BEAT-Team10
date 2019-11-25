from PyQt5 import QtCore, QtWidgets
from model import Plugin, DBConnection
from view.pop.ErrorDialog import ErrorDialog


class PluginTabController(QtCore.QObject):
    pluginSignal = QtCore.pyqtSignal()

    def __init__(self, plugin_tab):
        super().__init__()
        self.plugin_tab = plugin_tab
        self.plugin = ""

    def establish_connections(self):
        self.plugin_tab.pushButton_7.clicked.connect(self.create_plugin)
        self.plugin_tab.ButtonSavePlugin.clicked.connect(self.save_plugin)
        self.plugin_tab.ButtonDeletePlugin.clicked.connect(self.delete_plugin)
        self.plugin_tab.listWidget.itemSelectionChanged.connect(self.item_activated)
        self.plugin_tab.lineEdit.textChanged.connect(
            lambda x: self.search_installed_plugins(self.plugin_tab.lineEdit.text()))

    def establish_calls(self):
        self.set_plugins()

    def set_plugins(self):
        self.plugin_tab.listWidget.clear()
        for pl in Plugin.get_installed_plugins():
            self.plugin_tab.listWidget.addItem(pl)

    def create_plugin(self):
        text, ok_pressed = QtWidgets.QInputDialog.getText(self.plugin_tab, "Create New Plugin", "Name of Plugin:",
                                                          QtWidgets.QLineEdit.Normal, "")
        if ok_pressed and text != '':
            db_names = DBConnection.get_collection("plugin")
            coll = db_names.list_collections()
            for i in coll:
                if text in i:
                    x = ErrorDialog(self.plugin_tab, "Plugin with that name already exists", "Error Creating Plugin")
                    x.exec_()
                    return
            self.plugin_tab.DPVPluginDescription.setText("")
            self.plugin_tab.DPVPluginName.setText(text)
            self.plugin_tab.DVPPointOfInterest.setText("")
            self.plugin_tab.DPVDefaultOutputField.setText("")
            self.plugin_tab.listWidget.addItem(text)
            item = self.plugin_tab.listWidget.findItems(text, QtCore.Qt.MatchExactly)
            self.plugin_tab.listWidget.setCurrentItem(item[0])

    def save_plugin(self):
        plugin_db = DBConnection.get_collection("plugin")
        plg_cllc = plugin_db[self.plugin_tab.DPVPluginName.text()]
        info = {"name": self.plugin_tab.DPVPluginName.text(),
                "desc": self.plugin_tab.DPVPluginDescription.toPlainText(),
                "poi": {"item": ""}, "output": self.plugin_tab.DPVDefaultOutputField.text()}
        plg = Plugin.get_name(self.plugin_tab.DPVPluginName.text())
        if not plg:
            plg_cllc.insert(info, check_keys=False)
            x = ErrorDialog(self.plugin_tab, "Plugin Saved", "Save Plugin")
            x.exec_()
            self.pluginSignal.emit()
        else:
            x = ErrorDialog(self, "Plugin already exists", "Error Plugin")
            x.exec_()
            return

    def delete_plugin(self):
        if self.plugin != "":
            button_reply = QtWidgets.QMessageBox.question(self.plugin_tab, 'PyQt5 message',
                                                          "Do you like to erase Plugin %s ?" % self.plugin,
                                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                          QtWidgets.QMessageBox.No)
            if button_reply == QtWidgets.QMessageBox.Yes:
                project_db = DBConnection.get_collection("plugin")
                project_db.drop_collection(self.plugin)
                self.plugin = ""
                self.plugin_tab.DPVPluginDescription.setText("")
                self.plugin_tab.DPVPluginName.setText("")
                self.plugin_tab.DVPPointOfInterest.setText("")
                self.plugin_tab.DPVDefaultOutputField.setText("")
                list_items = self.plugin_tab.listWidget.selectedItems()
                if not list_items:
                    return
                for item in list_items:
                    self.plugin_tab.listWidget.takeItem(self.plugin_tab.listWidget.row(item))
        else:
            x = ErrorDialog(self.plugin_tab, "Please select a plugin", "Error")
            x.exec_()

    def item_activated(self):
        if self.plugin_tab.listWidget.count() != 0:
            plugin_s = self.plugin_tab.listWidget.selectedItems()
            plugin_name = [item.text().encode("ascii") for item in plugin_s]
            if plugin_name:
                try:
                    self.plugin = plugin_name[0].decode()
                    cursor = Plugin.get_name(self.plugin)
                    if cursor:
                        for pl in cursor:
                            self.plugin_tab.DPVPluginName.setText(pl["name"])
                            self.plugin_tab.DPVPluginDescription.setText(pl["desc"])
                            self.plugin_tab.DPVDefaultOutputField.setText(pl["output"])
                            for i in pl["poi"]["item"]:
                                last_text = self.plugin_tab.DVPPointOfInterest.toPlainText()
                                new = last_text + i["type"] + " " + i["name"] + "\n"
                                self.plugin_tab.DVPPointOfInterest.setText(new)
                except Exception as e:
                    x = ErrorDialog(self.plugin_tab, str(e), "Error")
                    x.exec_()

    def search_installed_plugins(self, text):
        if len(text) is not 0:
            search_result = self.plugin_tab.listWidget.findItems(text, QtCore.Qt.MatchContains)
            for item_index in range(self.plugin_tab.listWidget.count()):
                self.plugin_tab.listWidget.item(item_index).setHidden(True)
            for item_index in search_result:
                item_index.setHidden(False)
        else:
            for item_index in range(self.plugin_tab.listWidget.count()):
                self.plugin_tab.listWidget.item(item_index).setHidden(False)
