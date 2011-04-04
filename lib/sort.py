# -*- coding: utf-8 -*-

import os
import re
import xbmc
import xbmcaddon
from stat import *
from operator import itemgetter
from urllib import quote_plus, unquote_plus

MOVIES, TV_EPISODES, MUSIC_VIDEOS = range(3)

libraryList =((MOVIES, "Movies", "DefaultMovies.png"),
              (TV_EPISODES, "TV Episodes", "DefaultTVShows.png"),
              (MUSIC_VIDEOS, "Music Videos", "DefaultMusicVideos.png"),
             )

Addon = xbmcaddon.Addon(id=os.path.basename(os.getcwd()))

class Sort:

    def __init__(self, library):
        if(Addon.getSetting('debug')):
            self.debug = True

        self.library = libraryList[library][0]

        max_item_id = self.get_max_item_id()
        max_file_id = self.get_max_file_id()
        item_list   = self.get_items()

        # iterate through each item, sorting by ctime, then update
    # the item's id in the database
        i = 0
        count = len(item_list)
        for item in sorted(item_list, key=itemgetter(0)):
            (ctime, old_idItem, old_idFile, fullFilePath) = (item[0], item[1], item[2], item[3])
            i += 1
            new_idItem = max_item_id + i
            new_idFile  = max_file_id + i
            if self.debug:
                xbmc.log("ctime: %d old_idItem: %d new_idItem: %d old_idFile: %d new_idFile: %d file: %s" %
                         (ctime, old_idItem, new_idItem, old_idFile, new_idFile, fullFilePath))
            self.update_item_and_file_id(old_idItem, new_idItem, old_idFile, new_idFile)

        xbmc.log('script.sort-media addon run complete')

    def get_max_item_id(self):
        if self.library == MOVIES:
            get_maxid_sql = "select max(idMovie) from movieview"
        elif self.library == TV_EPISODES:
            get_maxid_sql = "select max(idEpisode) from episodeviev"
        elif self.library == MUSIC_VIDEOS:
            get_maxid_sql = "select max(idMVideo) from musicvideoview"

        if self.library in (MOVIES, TV_EPISODES, MUSIC_VIDEOS):
            sql_result = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( get_maxid_sql ), )
        return int((re.findall( "<field>(.+?)</field>", sql_result, re.DOTALL ))[0])

    def get_max_file_id(self):
        get_maxid_sql = "select max(idFile) from files"
        if self.library in (MOVIES, TV_EPISODES, MUSIC_VIDEOS):
            sql_result = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( get_maxid_sql ), )
        return int((re.findall( "<field>(.+?)</field>", sql_result, re.DOTALL ))[0])

    def get_items(self):
        """ fetch the idItem, idFile, and path+filename of all items in
            the Library, then stat each file to get the CTIME
            (creation time).  Returns a list of tuples containing
              (ctime, idItem, idFile, filename)
            eg:

            [ (12312312312, 1, 5, "c:/Movies/Gladiator (2000)/gladiator.mkv"),
              (12423234223, 2, 4, "smb://user:pass@server/Movies/Something (2010)/something.avi") ]
        """
        item_list = []
        xbmc.executehttpapi( "SetResponseFormat()" )
        xbmc.executehttpapi( "SetResponseFormat(OpenRecord,%s)" % ( "<record>", ) )
        xbmc.executehttpapi( "SetResponseFormat(CloseRecord,%s)" % ( "</record>", ) )

        if self.library == MOVIES:
            items_sql = "select idMovie,idFile,strPath,strFileName from movieview"
        elif self.library == TV_EPISODES:
            items_sql = "select idEpisode,idFile,strPath,strFileName from episodeview"
        elif self.library == MUSIC_VIDEOS:
            items_sql = "select idMVideo,idFile,strPath,strFileName from musicvideoview"
        if self.library in (MOVIES, TV_EPISODES, MUSIC_VIDEOS):
            sql_result = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( items_sql ), )
        records = re.findall( "<record>(.+?)</record>", sql_result, re.DOTALL )
        for record in records:
            fields = re.findall( "<field>(.*?)</field>", record, re.DOTALL )
            idItem = int(fields[0])
            idFile  = int(fields[1])
            strPath = xbmc.makeLegalFilename(fields[2])
            strFileName = xbmc.makeLegalFilename(fields[3])
            fullFilePath = xbmc.makeLegalFilename(os.path.join(strPath, strFileName))
            try:
                ctime = os.stat(fullFilePath)[ST_CTIME]
                item_list.append( (ctime, idItem, idFile, fullFilePath) )
            except OSError, e:
                xbmc.log("OSerror: %s, file: %s" % (e.strerror, e.filename))
        return item_list

    def update_item_and_file_id(self, old_idItem, new_idItem, old_idFile, new_idFile):
        if self.library == MOVIES:
            update_sql = ("update movie set idMovie=%(newItemId)d, idFile=%(newFileId)d where idMovie=%(oldItemId)d; " \
                          "update actorlinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update countrylinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update directorlinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update genrelinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update movielinktvshow set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update setlinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update studiolinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update writerlinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " %
                          {'newItemId': new_idItem, 'newFileId': new_idFile, 'oldItemId': old_idItem})

        elif self.library == TV_EPISODES:
            update_sql = ("update episode set idMovie=%(newItemId)d, idFile=%(newFileId)d where idMovie=%(oldItemId)d; " \
                          "update actorlink episode set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update directorlinkepisode set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update tvshowlinkepisode set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update writerlinkepisode set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " %
                          {'newItemId': new_idItem, 'newFileId': new_idFile, 'oldItemId': old_idItem})

        elif self.library == MUSIC_VIDEOS:
            update_sql = ("update musicvideo set idMovie=%(newItemId)d, idFile=%(newFileId)d where idMovie=%(oldItemId)d; " \
                          "update actorlinkmusicvideo set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update directorlinkmusicvideo set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update genrelinkmusicvideo set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " \
                          "update studiolinkmusicvideo set idMovie=%(newItemId)d where idMovie=%(oldItemId)d; " %
                          {'newItemId': new_idItem, 'newFileId': new_idFile, 'oldItemId': old_idItem})

        if self.library in (MOVIES, TV_EPISODES, MUSIC_VIDEOS):
            xbmc.executehttpapi( "ExecVideoDatabase(%s)" % quote_plus( update_sql ), )

            update_sql = ("update files set idFile=%(newFileId)d where idFile=%(oldFileId)d; " \
                          "update bookmark set idFile=%(newFileId)d where idFile=%(oldFileId)d; " \
                          "update stacktimes set idFile=%(newFileId)d where idFile=%(oldFileId)d; " \
                          "update streamdetails set idFile=%(newFileId)d where idFile=%(oldFileId)d; " %
                          {'newFileId': new_idFile, 'oldFileId': old_idFile})
            xbmc.executehttpapi( "ExecVideoDatabase(%s)" % quote_plus( update_sql ), )
