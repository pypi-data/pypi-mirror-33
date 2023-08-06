#!/usr/bin/python
# -*- coding: utf-8 -*-

# Cagou: desktop/mobile frontend for Salut à Toi XMPP client
# Copyright (C) 2016-2018 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from sat.core import log as logging
log = logging.getLogger(__name__)
from sat.core.i18n import _
from cagou.core.constants import Const as C
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.metrics import sp, dp
from kivy import properties
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.quick_frontend import quick_chat
from sat_frontends.tools import jid
from cagou.core import cagou_widget
from cagou.core.image import Image
from cagou.core.common import SymbolButton, JidButton
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from cagou import G
import mimetypes


PLUGIN_INFO = {
    "name": _(u"chat"),
    "main": "Chat",
    "description": _(u"instant messaging with one person or a group"),
    "icon_symbol": u"chat",
}

# following const are here temporary, they should move to quick frontend
OTR_STATE_UNTRUSTED = 'untrusted'
OTR_STATE_TRUSTED = 'trusted'
OTR_STATE_TRUST = (OTR_STATE_UNTRUSTED, OTR_STATE_TRUSTED)
OTR_STATE_UNENCRYPTED = 'unencrypted'
OTR_STATE_ENCRYPTED = 'encrypted'
OTR_STATE_ENCRYPTION = (OTR_STATE_UNENCRYPTED, OTR_STATE_ENCRYPTED)


class MessAvatar(Image):
    pass


class MessageWidget(BoxLayout):
    mess_data = properties.ObjectProperty()
    mess_xhtml = properties.ObjectProperty()
    mess_padding = (dp(5), dp(5))
    avatar = properties.ObjectProperty()
    delivery = properties.ObjectProperty()
    font_size = properties.NumericProperty(sp(12))

    def __init__(self, **kwargs):
        # self must be registered in widgets before kv is parsed
        kwargs['mess_data'].widgets.add(self)
        super(MessageWidget, self).__init__(**kwargs)
        avatar_path = self.mess_data.avatar
        if avatar_path is not None:
            self.avatar.source = avatar_path

    @property
    def chat(self):
        """return parent Chat instance"""
        return self.mess_data.parent

    @property
    def message(self):
        """Return currently displayed message"""
        return self.mess_data.main_message

    @property
    def message_xhtml(self):
        """Return currently displayed message"""
        return self.mess_data.main_message_xhtml

    def widthAdjust(self):
        """this widget grows up with its children"""
        pass
        # parent = self.mess_xhtml.parent
        # padding_x = self.mess_padding[0]
        # text_width, text_height = self.mess_xhtml.texture_size
        # if text_width > parent.width:
        #     self.mess_xhtml.text_size = (parent.width - padding_x, None)
        #     self.text_max = text_width
        # elif self.mess_xhtml.text_size[0] is not None and text_width  < parent.width - padding_x:
        #     if text_width < self.text_max:
        #         self.mess_xhtml.text_size = (None, None)
        #     else:
        #         self.mess_xhtml.text_size = (parent.width  - padding_x, None)

    def update(self, update_dict):
        if 'avatar' in update_dict:
            self.avatar.source = update_dict['avatar']
        if 'status' in update_dict:
            status = update_dict['status']
            self.delivery.text =  u'\u2714' if status == 'delivered' else u''


class MessageInputBox(BoxLayout):
    pass


class MessageInputWidget(TextInput):

    def _key_down(self, key, repeat=False):
        displayed_str, internal_str, internal_action, scale = key
        if internal_action == 'enter':
            self.dispatch('on_text_validate')
        else:
            super(MessageInputWidget, self)._key_down(key, repeat)


class MessagesWidget(GridLayout):
    pass


class EncryptionButton(SymbolButton):

    def __init__(self, chat, **kwargs):
        """
        @param chat(Chat): Chat instance
        """
        self.chat = chat
        # for now we do a simple ContextMenu as we have only OTR
        self.otr_menu = OtrMenu(chat)
        super(EncryptionButton, self).__init__(**kwargs)
        self.bind(on_release=self.otr_menu.open)

    def getColor(self):
        if self.chat.otr_state_encryption == OTR_STATE_UNENCRYPTED:
            return  (0.4, 0.4, 0.4, 1)
        elif self.chat.otr_state_trust == OTR_STATE_TRUSTED:
            return (0.29,0.87,0.0,1)
        else:
            return  (0.4, 0.4, 0.4, 1)

    def getSymbol(self):
        if self.chat.otr_state_encryption == OTR_STATE_UNENCRYPTED:
            return 'lock-open'
        elif self.chat.otr_state_trust == OTR_STATE_TRUSTED:
            return 'lock-filled'
        else:
            return 'lock'


class OtrMenu(DropDown):

    def __init__(self, chat, **kwargs):
        """
        @param chat(Chat): Chat instance
        """
        self.chat = chat
        super(OtrMenu, self).__init__(**kwargs)

    def otr_start(self):
        self.dismiss()
        G.host.launchMenu(
            C.MENU_SINGLE,
            (u"otr", u"start/refresh"),
            {u'jid': unicode(self.chat.target)},
            None,
            C.NO_SECURITY_LIMIT,
            self.chat.profile
            )

    def otr_end(self):
        self.dismiss()
        G.host.launchMenu(
            C.MENU_SINGLE,
            (u"otr", u"end session"),
            {u'jid': unicode(self.chat.target)},
            None,
            C.NO_SECURITY_LIMIT,
            self.chat.profile
            )

    def otr_authenticate(self):
        self.dismiss()
        G.host.launchMenu(
            C.MENU_SINGLE,
            (u"otr", u"authenticate"),
            {u'jid': unicode(self.chat.target)},
            None,
            C.NO_SECURITY_LIMIT,
            self.chat.profile
            )


class Chat(quick_chat.QuickChat, cagou_widget.CagouWidget):
    message_input = properties.ObjectProperty()
    messages_widget = properties.ObjectProperty()

    def __init__(self, host, target, type_=C.CHAT_ONE2ONE, nick=None, occupants=None, subject=None, profiles=None):
        quick_chat.QuickChat.__init__(self, host, target, type_, nick, occupants, subject, profiles=profiles)
        self.otr_state_encryption = OTR_STATE_UNENCRYPTED
        self.otr_state_trust = OTR_STATE_UNTRUSTED
        # completion attributes
        self._hi_comp_data = None
        self._hi_comp_last = None
        self._hi_comp_dropdown = DropDown()
        self._hi_comp_allowed = True
        cagou_widget.CagouWidget.__init__(self)
        if type_ == C.CHAT_ONE2ONE:
            self.encryption_btn = EncryptionButton(self)
            self.headerInputAddExtra(self.encryption_btn)
        self.header_input.hint_text = u"{}".format(target)
        self.host.addListener('progressError', self.onProgressError, profiles)
        self.host.addListener('progressFinished', self.onProgressFinished, profiles)
        self._waiting_pids = {}  # waiting progress ids
        self.postInit()

    def __unicode__(self):
        return u"Chat({})".format(self.target)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __repr__(self):
        return self.__str__()

    @classmethod
    def factory(cls, plugin_info, target, profiles):
        profiles = list(profiles)
        if len(profiles) > 1:
            raise NotImplementedError(u"Multi-profiles is not available yet for chat")
        if target is None:
            target = G.host.profiles[profiles[0]].whoami
        return G.host.widgets.getOrCreateWidget(cls, target, on_new_widget=None, on_existing_widget=C.WIDGET_RECREATE, profiles=profiles)

    ## header ##

    def changeWidget(self, jid_):
        """change current widget for a new one with given jid

        @param jid_(jid.JID): jid of the widget to create
        """
        plugin_info = G.host.getPluginInfo(main=Chat)
        factory = plugin_info['factory']
        G.host.switchWidget(self, factory(plugin_info, jid_, profiles=[self.profile]))
        self.header_input.text = ''

    def onHeaderInput(self):
        text = self.header_input.text.strip()
        try:
            if text.count(u'@') != 1 or text.count(u' '):
                raise ValueError
            jid_ = jid.JID(text)
        except ValueError:
            log.info(u"entered text is not a jid")
            return

        def discoCb(disco):
            # TODO: check if plugin XEP-0045 is activated
            if "conference" in [i[0] for i in disco[1]]:
                G.host.bridge.mucJoin(unicode(jid_), "", "", self.profile, callback=self._mucJoinCb, errback=self._mucJoinEb)
            else:
                self.changeWidget(jid_)

        def discoEb(failure):
            log.warning(u"Disco failure, ignore this text: {}".format(failure))

        G.host.bridge.discoInfos(jid_.domain, self.profile, callback=discoCb, errback=discoEb)

    def onHeaderInputCompleted(self, input_wid, completed_text):
        self._hi_comp_allowed = False
        input_wid.text = completed_text
        self._hi_comp_allowed = True
        self._hi_comp_dropdown.dismiss()
        self.onHeaderInput()

    def onHeaderInputComplete(self, wid, text):
        if not self._hi_comp_allowed:
            return
        text = text.lstrip()
        if not text:
            self._hi_comp_data = None
            self._hi_comp_last = None
            self._hi_comp_dropdown.dismiss()
            return

        profile = list(self.profiles)[0]

        if self._hi_comp_data is None:
            # first completion, we build the initial list
            comp_data = self._hi_comp_data = []
            self._hi_comp_last = ''
            for jid_, jid_data in G.host.contact_lists[profile].all_iter:
                comp_data.append((jid_, jid_data))
            comp_data.sort(key=lambda datum: datum[0])
        else:
            comp_data = self._hi_comp_data

        # XXX: dropdown is rebuilt each time backspace is pressed or if the text is changed,
        #      it works OK, but some optimisation may be done here
        dropdown = self._hi_comp_dropdown

        if not text.startswith(self._hi_comp_last) or not self._hi_comp_last:
            # text has changed or backspace has been pressed, we restart
            dropdown.clear_widgets()

            for jid_, jid_data in comp_data:
                nick = jid_data.get(u'nick', u'')
                if text in jid_.bare or text in nick.lower():
                    btn = JidButton(
                        jid = jid_.bare,
                        profile = profile,
                        size_hint = (0.5, None),
                        nick = nick,
                        on_release=lambda dummy, txt=jid_.bare: self.onHeaderInputCompleted(wid, txt)
                        )
                    dropdown.add_widget(btn)
        else:
            # more chars, we continue completion by removing unwanted widgets
            to_remove = []
            for c in dropdown.children[0].children:
                if text not in c.jid and text not in (c.nick or ''):
                    to_remove.append(c)
            for c in to_remove:
                dropdown.remove_widget(c)
        if dropdown.attach_to is None:
            dropdown.open(wid)
        self._hi_comp_last = text

    def messageDataConverter(self, idx, mess_id):
        return {"mess_data": self.messages[mess_id]}

    def _onHistoryPrinted(self):
        """Refresh or scroll down the focus after the history is printed"""
        # self.adapter.data = self.messages
        for mess_data in self.messages.itervalues():
            self.appendMessage(mess_data)
        super(Chat, self)._onHistoryPrinted()

    def createMessage(self, message):
        self.appendMessage(message)

    def appendMessage(self, mess_data):
        self.messages_widget.add_widget(MessageWidget(mess_data=mess_data))
        self.notify(mess_data)

    def _get_notif_msg(self, mess_data):
        return _(u"{nick}: {message}").format(
            nick=mess_data.nick,
            message=mess_data.main_message)

    def notify(self, mess_data):
        """Notify user when suitable

        For one2one chat, notification will happen when window has not focus
        or when one2one chat is not visible. A note is also there when widget
        is not visible.
        For group chat, note will be added on mention, with a desktop notification if
        window has not focus.
        """
        visible_clones = [w for w in G.host.getVisibleList(self.__class__) if w.target == self.target]
        if len(visible_clones) > 1 and visible_clones.index(self) > 0:
            # to avoid multiple notifications in case of multiple cloned widgets
            # we only handle first clone
            return
        is_visible = bool(visible_clones)
        if self.type == C.CHAT_ONE2ONE:
            if (not Window.focus or not is_visible) and not mess_data.history:
                notif_msg = self._get_notif_msg(mess_data)
                G.host.desktop_notif(
                    notif_msg,
                    title=_(u"private message"))
                if not is_visible:
                    G.host.addNote(
                        _(u"private message"),
                        notif_msg
                        )
        else:
            if mess_data.mention and not mess_data.history:
                notif_msg = self._get_notif_msg(mess_data)
                G.host.addNote(
                    _(u"mention"),
                    notif_msg
                    )
                if not Window.focus:
                    G.host.desktop_notif(
                        notif_msg,
                        title=_(u"mention ({room_jid})").format(
                            room_jid=self.target)
                        )

    def onSend(self, input_widget):
        G.host.messageSend(
            self.target,
            {'': input_widget.text}, # TODO: handle language
            mess_type = C.MESS_TYPE_GROUPCHAT if self.type == C.CHAT_GROUP else C.MESS_TYPE_CHAT, # TODO: put this in QuickChat
            profile_key=self.profile
            )
        input_widget.text = ''

    def onProgressFinished(self, progress_id, metadata, profile):
        try:
            callback, cleaning_cb = self._waiting_pids.pop(progress_id)
        except KeyError:
            return
        if cleaning_cb is not None:
            cleaning_cb()
        callback(metadata, profile)

    def onProgressError(self, progress_id, err_msg, profile):
        try:
            dummy, cleaning_cb = self._waiting_pids[progress_id]
        except KeyError:
            return
        else:
            del self._waiting_pids[progress_id]
            if cleaning_cb is not None:
                cleaning_cb()
        # TODO: display message to user
        log.warning(u"Can't transfer file: {}".format(err_msg))

    def fileTransferDone(self, metadata, profile):
        log.debug("file transfered: {}".format(metadata))
        extra = {}

        # FIXME: Q&D way of getting file type, upload plugins shouls give it
        mime_type = mimetypes.guess_type(metadata['url'])[0]
        if mime_type is not None:
            if mime_type.split(u'/')[0] == 'image':
                # we generate url ourselves, so this formatting is safe
                extra['xhtml'] = u"<img src='{url}' />".format(**metadata)

        G.host.messageSend(
            self.target,
            {'': metadata['url']},
            mess_type = C.MESS_TYPE_GROUPCHAT if self.type == C.CHAT_GROUP else C.MESS_TYPE_CHAT,
            extra = extra,
            profile_key=profile
            )

    def fileTransferCb(self, progress_data, cleaning_cb):
        try:
            progress_id = progress_data['progress']
        except KeyError:
            xmlui = progress_data['xmlui']
            G.host.showUI(xmlui)
        else:
            self._waiting_pids[progress_id] = (self.fileTransferDone, cleaning_cb)

    def onTransferOK(self, file_path, cleaning_cb, transfer_type):
        if transfer_type == C.TRANSFER_UPLOAD:
            G.host.bridge.fileUpload(
                file_path,
                "",
                "",
                {"ignore_tls_errors": C.BOOL_TRUE},  # FIXME: should not be the default
                self.profile,
                callback = lambda progress_data: self.fileTransferCb(progress_data, cleaning_cb)
                )
        elif transfer_type == C.TRANSFER_SEND:
            if self.type == C.CHAT_GROUP:
                log.warning(u"P2P transfer is not possible for group chat")
                # TODO: show an error dialog to user, or better hide the send button for MUC
            else:
                jid_ = self.target
                if not jid_.resource:
                    jid_ = G.host.contact_lists[self.profile].getFullJid(jid_)
                G.host.bridge.fileSend(unicode(jid_), file_path, "", "", profile=self.profile)
                # TODO: notification of sending/failing
        else:
            raise log.error(u"transfer of type {} are not handled".format(transfer_type))


    def _mucJoinCb(self, joined_data):
        joined, room_jid_s, occupants, user_nick, subject, profile = joined_data
        self.host.mucRoomJoinedHandler(*joined_data[1:])
        jid_ = jid.JID(room_jid_s)
        self.changeWidget(jid_)

    def _mucJoinEb(self, failure):
        log.warning(u"Can't join room: {}".format(failure))

    def _onDelete(self):
        self.host.removeListener('progressFinished', self.onProgressFinished)
        self.host.removeListener('progressError', self.onProgressError)
        return super(Chat, self).onDelete()

    def onOTRState(self, state, dest_jid, profile):
        assert profile in self.profiles
        if state in OTR_STATE_ENCRYPTION:
            self.otr_state_encryption = state
        elif state in OTR_STATE_TRUST:
            self.otr_state_trust = state
        else:
            log.error(_(u"Unknown OTR state received: {}".format(state)))
            return
        self.encryption_btn.symbol = self.encryption_btn.getSymbol()
        self.encryption_btn.color = self.encryption_btn.getColor()

    def onDelete(self, force=False):
        if force==True:
            return self._onDelete()
        if len(list(G.host.widgets.getWidgets(self.__class__, self.target, profiles=self.profiles))) > 1:
            # we don't keep duplicate widgets
            return self._onDelete()
        return False


PLUGIN_INFO["factory"] = Chat.factory
quick_widgets.register(quick_chat.QuickChat, Chat)
