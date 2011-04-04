# -*- coding: utf-8 -*-

import os
import xbmcgui, xbmcaddon

from lib.sort import libraryList, Sort

addon = xbmcaddon.Addon("script.sort-media")
SOURCEPATH = addon.getAddonInfo('path')
ACTION_PREVIOUS_MENU = 10

class SortDialog(xbmcgui.WindowXMLDialog):

    def onInit(self):
        self.getControl(1).setLabel("Select library to be sorted")
        self.getControl(5).setVisible(False)
        self.list = self.getControl(6)
        self.library = None

        for item in libraryList:
            listitem = xbmcgui.ListItem(item[1], iconImage=item[2])
            self.list.addItem(listitem)

        self.setFocus(self.list)

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID in (3, 6):
            self.library = self.list.getSelectedPosition()
            self.close()

    def onFocus(self, controlID):
        pass

if __name__ == '__main__':
    w = SortDialog("DialogSelect.xml", SOURCEPATH)
    w.doModal()

    if w.library is not None:
      Sort(w.library)

    del w