# -*- coding: utf-8 -*- #
"""
分析扫描软件的位置版本图标等信息
注意32和64 KEY 都要扫描

"""
import os
import winreg

import win32ui
import win32file
import win32api
import win32gui
from win32con import *


class IconBase(object):
    def __init__(self):
        super(IconBase, self).__init__()
        self.serach_path_lst = []

    def set_serach_lst(self, data):
        self.serach_path_lst = data
        self.get_app_icon = self.get_app_icon_by_serach

    def bitmapFromHIcon(self, hIcon):
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, 48, 48)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        hdc.DrawIcon((8, 8), hIcon)
        hdc.DeleteDC()
        return hbmp.GetHandle()

    def __get_app_icon__(self, root, filename):
        from PyQt5.QtGui import QPixmap
        large, small = win32gui.ExtractIconEx(filename, 0)
        l = QPixmap.fromWinHBITMAP(self.bitmapFromHIcon(large[0]), 2)
        s = QPixmap.fromWinHBITMAP(self.bitmapFromHIcon(small[0]), 2)

        win32gui.DestroyIcon(large[0])
        win32gui.DestroyIcon(small[0])

        return {'large': l, 'small': s}

    def get_app_icon(self, root, filename):
        return self.__get_app_icon__(root, filename)

    def get_app_icon_by_serach(self, root, filename):
        for a in self.serach_path_lst:
            if os.path.exists(a.format(root)):
                pixmap = a.format(root)
                if os.path.getsize(pixmap) < 5000:
                    return self.__get_app_icon__(root, filename)

                return {'large': pixmap, 'small': pixmap}


class FindBase(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inst'):
            cls._inst = super(FindBase, cls).__new__(cls, *args, **kwargs)
            cls._inst.init()
        return cls._inst

    def __init__(self):
        super(FindBase, self).__init__()
        self.dont_del = True

    def init(self):
        self.runed = False
        self.data = []

    def get_data(self):
        return self.data

    def get_data_by_version(self, version, bit):
        for a in self.data:
            if a['version_string'] == '3dsmax {}'.format(version) and a['bit'] == bit:
                return a

    def run(self):
        if self.runed:
            return

        self.find()
        self.runed = True

    def find_value(self, key_path, found_lst, flag=KEY_WOW64_64KEY, value_name='Installdir', key_name=None,
                   spcae=winreg.HKEY_LOCAL_MACHINE):

        if key_name:
            if os.path.basename(key_path) == key_name:
                open_key = winreg.OpenKey(spcae, key_path, 0, KEY_ALL_ACCESS | flag)
                data = win32api.RegQueryValue(open_key, '')
                if data:
                    found_lst.append(data)

        try:
            open_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, KEY_ALL_ACCESS | flag)
        except:
            return

        try:
            data = win32api.RegQueryValueEx(open_key, value_name)
            if data:
                found_lst.append(data[0])
        except:
            pass

        countkey = winreg.QueryInfoKey(open_key)[0]
        for i in range(int(countkey)):
            name = winreg.EnumKey(open_key, i)
            key_index = '\\'.join((key_path, name))
            self.find_value(key_index, found_lst, flag, value_name, key_name)

        return found_lst

    def get_app_version(self, file_name):
        try:
            info = win32api.GetFileVersionInfo(file_name, os.sep)

            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            version = '%d.%d.%d.%04d' % (
                win32api.HIWORD(ms),
                win32api.LOWORD(ms),
                win32api.HIWORD(ls),
                win32api.LOWORD(ls))
            return version

        except BaseException as e:
            return 0

    def get_app_bit(self, filename):
        try:
            type = win32file.GetBinaryType(filename)
            if type == 0:
                return "32"
            elif type == 6:
                return "64"
        except BaseException as e:
            return '?'

    def get_app_icon(self, root, filename, found_lst=None):
        obj = IconBase()
        if found_lst:
            obj.set_serach_lst(found_lst)

        data = obj.get_app_icon(root, filename)
        return data


class Autodesk3dsMaxCollect(FindBase):
    def __str__(self):
        return 'Autodesk 3dsmax'

    def find(self):
        unkey = []

        icon_found_path = (
            '{}UI/Icons/icon_main.ico',
            '{}ui/Icons/ATS/atsscene.ico',
            '{}UI_ln/Icons/ATS/ATSScene.ico',
        )
        # find by os env
        for env_name in os.environ:
            if 'ADSK_3DSMAX' in env_name:
                root = os.environ[env_name]
                full_path = os.path.join(root, '3dsmax.exe')
                if os.path.exists(full_path):
                    bit, version = self.get_app_bit(full_path), self.get_app_version(full_path)
                    version_str = str(2000 + (int(version.split('.')[0]) - 2))
                    if int(version.split('.')[0]) < 10:
                        version_str = str(('.'.join(version.split('.')[:2])))

                    icon = self.get_app_icon(root, full_path, icon_found_path)

                    max_data = {'path': full_path,
                                'bit': bit,
                                'icon': icon,
                                'version': int(version.replace('.', '')),
                                'version_string': '3dsmax {}'.format(version_str)
                                }

                    from cgtools.Autodesk3dsmax import Autodesk3dsmax
                    max_obj = Autodesk3dsmax()
                    max_obj.ready_data_from_finder(max_data)
                    if full_path not in unkey:
                        self.data.append(max_obj)
                        unkey.append(full_path)

        # find by reg
        found_lst = []
        self.find_value("SOFTWARE\\Autodesk\\3dsMax\\", found_lst, flag=KEY_WOW64_64KEY)
        self.find_value("SOFTWARE\\Autodesk\\3dsMax\\", found_lst, flag=KEY_WOW64_32KEY)
        for root in found_lst:
            full_path = os.path.join(root, '3dsmax.exe')
            if os.path.exists(full_path):

                bit = self.get_app_bit(full_path)
                version = self.get_app_version(full_path)
                version_str = str(2000 + (int(version.split('.')[0]) - 2))
                if int(version.split('.')[0]) < 10:
                    version_str = str(('.'.join(version.split('.')[:2])))
                icon = self.get_app_icon(root, full_path, icon_found_path)

                max_data = {'path': full_path,
                            'bit': bit,
                            'icon': icon,
                            'version': int(version.replace('.', '')),
                            'version_string': '3dsmax {}'.format(version_str)
                            }

                from cgtools.Autodesk3dsmax import Autodesk3dsmax
                max_obj = Autodesk3dsmax()
                max_obj.ready_data_from_finder(max_data)

                if full_path not in unkey:
                    self.data.append(max_obj)
                    unkey.append(full_path)


if __name__ == '__main__':
    a = Autodesk3dsMaxCollect()
    a.run()

    import pprint

    pprint.pprint(a.data)
