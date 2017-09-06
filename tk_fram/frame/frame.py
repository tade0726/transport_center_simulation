# -*- coding: utf-8 -*-

from tkinter import Frame
from tkinter.ttk import Combobox
from tkinter import Checkbutton, Entry
from tkinter import IntVar, StringVar, DISABLED, NORMAL
from .frame_view import ConfigFrame, NUM_TRANSLATE_DICT, ENTRY_STATUS_DIC, \
    M_R_DICT, CACHE_INSTANCE_DICT, CURRENT


class App(Frame):
    """"""
    def __init__(self, master=None, pack: dict=None, attr: dict=None,
                 xlayout: tuple=(0, ), ylayout: tuple=(0, )):
        super().__init__(master=master)
        self.pack_dic = pack
        self.attr = attr
        self.xlayout = xlayout
        self.ylayout = ylayout
        self._init_frame()

    def _init_frame(self):
        if self.pack_dic:
            self.grid(self.pack_dic)
            self.rowconfigure(self.ylayout, weight=1)
            self.columnconfigure(self.xlayout, weight=1)
        else:
            self.grid()
        if self.attr:
            self.config(self.attr)


class ComboboxCreate(Combobox):

    def __init__(
            self,
            master=None,
            string_combobox=None,
            list_var: list=None,
            attr_dic: dict=None,
            grid_dic: dict=None
    ):
        super().__init__(master=master)
        self.string = string_combobox
        self.list_var = list_var
        self.attr_dic = attr_dic
        self.grid_dic = grid_dic
        self._update_config()
        self._init_combobox_list()

    def _update_config(self):
        self.attr_dic.update(
            {
                'textvariable': self.string,
                'values': self.list_var
            }
        )

    def _init_combobox_list(self):
        """"""
        if self.attr_dic:
            self.config(self.attr_dic)
        #
        if self.grid_dic:
            self.grid(self.grid_dic)
        else:
            self.grid()


class EntryCreate(Entry):
    """"""

    def __init__(
            self,
            master=None,
            grid_dic: dict = None,
            attr_dic: dict = None,
            text_var=None,
    ):
        super().__init__(master=master)
        self.attr_dic = attr_dic
        self.grid_dic = grid_dic
        self.text_var = text_var
        self._update_config()
        self._init_entry()

    def _update_config(self):
        self.attr_dic.update(
            {
                'textvariable': self.text_var
            }
        )

    def _init_entry(self):
        """"""
        if self.attr_dic:
            self.config(self.attr_dic)
        #
        if self.grid_dic:
            self.grid(self.grid_dic)
        else:
            self.grid()


class CheckBtnCreate(Checkbutton):
    """"""
    def __init__(
            self,
            master=None,
            grid_dic: dict=None,
            attr_dic: dict=None,
            w_id: str='',
            var=None,
            command=None
    ):
        """"""
        super().__init__(master=master)
        self.grid_dic = grid_dic
        self.attr_dic = attr_dic
        self.text = w_id
        self.var = var
        self.command = command
        self._update_config()
        self._init_check_btn()

    def _update_config(self):
        self.attr_dic.update({
            'text': self.text,
            'variable': self.var,
            'command': self.command})

    def _init_check_btn(self):
        """"""
        if self.attr_dic:
            self.config(self.attr_dic)
        if self.grid_dic:
            self.grid(self.grid_dic)
        else:
            self.grid()

    def append_cls(
            self,
            cls=Entry,
            var=None,
            attr: dict=None,
            grid: dict=None
    ):
        """附加"""
        return_cls = cls(master=self.master)
        attr_config = attr.update({
            'textvariable': var})
        return_cls.config(attr_config)
        return_cls.grid(grid)

        return return_cls


def init_check_btn(master, w_id, var, command):
    """"""
    return CheckBtnCreate(
        master=master,
        grid_dic=ConfigFrame.CHECK_BTN[w_id]['grid'],
        attr_dic=ConfigFrame.CHECK_BTN[w_id]['attr'],
        w_id=w_id,
        var=var,
        command=command
    )


def init_combobox_list(master, w_id, string_combobox, list_var):
    """

    :param master:
    :param w_id:
    :param string_combobox:
    :param list_var:
    :return:
    """
    return ComboboxCreate(
        master=master,
        string_combobox=string_combobox,
        list_var=list_var,
        attr_dic=ConfigFrame.COMBOBOX_LIST[w_id]['attr'],
        grid_dic=ConfigFrame.COMBOBOX_LIST[w_id]['grid']
    )


def init_entry(master, w_id, text_var):
    """

    :param master:
    :param w_id:
    :param text_var:
    :return:
    """
    return EntryCreate(
        master=master,
        attr_dic=ConfigFrame.ENTRY[w_id]['attr'],
        grid_dic=ConfigFrame.ENTRY[w_id]['grid'],
        text_var=text_var
    )


class CheckBtnEntryList(object):

    def __init__(self, w_id, master, list_value):
        self.w_id = w_id
        self.master = master
        self.list_value = list_value
        self.var = IntVar()
        self.string = StringVar()
        self.string_combobox = IntVar()
        self.init_list = self.init_list()
        self.entry = self.init_entry()
        self.check_btn = self.init_check_btn()

    @property
    def _list_value(self):
        if self.w_id == 'j41_1' or self.w_id == 'h3_1':
            return self.list_value[1]
        if 'j' in self.w_id or 'h' in self.w_id:
            return self.list_value[0]
        return self.list_value

    @property
    def combobox_value(self):
        key = self.w_id[0].upper()
        if key in NUM_TRANSLATE_DICT:
            return int(CACHE_INSTANCE_DICT[
                           CURRENT['TIME']['start_time']
                       ][self.w_id]['num']) * NUM_TRANSLATE_DICT[key]
        else:
            return CACHE_INSTANCE_DICT[
                CURRENT['TIME']['start_time']
            ][self.w_id]['num']

    def init_list(self):
        return init_combobox_list(
            master=self.master,
            w_id=self.w_id,
            string_combobox=self.string_combobox,
            list_var=self._list_value
        )

    def init_entry(self):
        return init_entry(
            master=self.master,
            w_id=self.w_id,
            text_var=self.string
        )

    def init_check_btn(self):
        return init_check_btn(
            master=self.master,
            w_id=self.w_id,
            var=self.var,
            command=self.chk_button_value
        )

    def init_on_off_status(self):
        self.set_status(CACHE_INSTANCE_DICT)

    def set_status(self, status_dict):
        if self.w_id == 'j41_1' or 'h' in self.w_id:
            self.var.set(1)
            self.string.set(ENTRY_STATUS_DIC[1])
            self.string_combobox.set(self.combobox_value)
            self.check_btn['state'] = DISABLED
            self.change_color(self.entry)
        # elif 'm' in self.w_id or 'j' in self.w_id:
        elif 'm' in self.w_id:
            # 判定 J 是否有缓存值且缓存值是否有效，否则取初始值(M 默认不匹配)
            # if self.w_id in CACHE_J_STATUS and \
            #                 CACHE_J_STATUS[self.w_id] != self.check_var:
            #     self.var.set(CACHE_J_STATUS[self.w_id])
            # else:
            #     self.var.set(self.check_var)
            self.var.set(self.check_var)
            self.string.set(ENTRY_STATUS_DIC[self.var.get()])
            self.change_combobox_status(self)
            self.change_color(self.entry)
            # if 'm' in self.w_id:
            self.check_btn['state'] = DISABLED
            # if 'j' in self.w_id:
            #     # 根据初始化的值判断是否为 DISABLED
            #     if self.check_var == 0 :
            #         self.check_btn['state'] = DISABLED
            #     else:
            #         self.check_btn['state'] = NORMAL
        else:
            self.var.set(
                status_dict[CURRENT['TIME']['start_time']][self.w_id]['status']
            )
            self.string.set(ENTRY_STATUS_DIC[self.var.get()])
            self.change_combobox_status(self)
            self.change_color(self.entry)

    def chk_button_value(self):
        # j 由 ON 改为 OFF 时将会添加到 J的缓存字典里
        # if 'j' in self.w_id:
        #     if self.var.get() == 0:
        #         CACHE_J_STATUS[self.w_id] = self.var.get()
        #         j_status_list = self.create_status_list()
        #         if len(j_status_list) == 1:
        #             CHECK_BTN_ENTRY_DIC[j_status_list[0]].check_btn[
        #                 'state'] = DISABLED
        #     else:
        #         j_status_list = self.create_status_list()
        #         if len(j_status_list) == 2:
        #             j_status_list.remove(self.w_id)
        #             CHECK_BTN_ENTRY_DIC[j_status_list[0]].check_btn[
        #                 'state'] = NORMAL
        #         CACHE_J_STATUS.pop(self.w_id)

        self.string.set(ENTRY_STATUS_DIC[self.var.get()])
        self.change_color(self.entry)
        self.change_combobox_status(self)

    # def create_status_list(self):
    #     j_status_list = []
    #     CACHE_J_STATUS[self.w_id] = self.var.get()
    #     for key, j_list in R_J_DICT.items():
    #         if self.w_id in j_list:
    #             for j_id in j_list:
    #                 if CHECK_BTN_ENTRY_DIC[j_id].var.get() == 1:
    #                     j_status_list.append(j_id)
    #             return j_status_list

    # 返回勾选框的状态值 0 或 1
    @property
    def check_var(self):
        return _init_m_j(self.w_id)

    @staticmethod
    def change_color(entry):
        if entry.text_var.get() == 'ON':
            entry['disabledforeground'] = 'blue'
        else:
            entry['disabledforeground'] = 'SystemDisabledText'

    @staticmethod
    def change_combobox_status(instance):
        instance.string_combobox.set(instance.combobox_value)
        if instance.var.get() == 0:
            instance.init_list['state'] = DISABLED
        else:
            instance.init_list['state'] = NORMAL


def _init_m_j(w_id):
    if 'm' in w_id:
        status = 0
        for i in M_R_DICT[w_id]:
            status = CACHE_INSTANCE_DICT[
                         CURRENT['TIME']['start_time']
                     ][i]['status'] or status
        return status
    # if 'j' in w_id and w_id != 'j41_1':
    #     j_status = 0
    #     for key, j_list in R_J_DICT.items():
    #         if w_id in j_list:
    #             j_status  =  CACHE_INSTANCE_DICT[
    #                              CURRENT['TIME']['start_time']
    #                          ][key]['status'] or j_status
    #     return j_status


def update_m_j():
    # 根据 R 的状态值，初始化 J 跟 M 的状态值，如果 J 有缓存，则取缓存值
    # for j in ConfigFrame.WIG_BTN_DICT['J'][:-1]:
    #     if j in CACHE_J_STATUS:
    #         CACHE_INSTANCE_DICT[CURRENT['TIME']['start_time']][j]['status']\
    #             = CACHE_J_STATUS[j]
    #     else:
    #         CACHE_INSTANCE_DICT[CURRENT['TIME']['start_time']][j]['status']\
    #             = _init_m_J(j)
    for m in ConfigFrame.WIG_BTN_DICT['M']:
        CACHE_INSTANCE_DICT[
            CURRENT['TIME']['start_time']
        ][m]['status'] = _init_m_j(m)