"""
KalamAI - "Your Words, Our Voice"
Multilingual TTS App v1.0.0
Uses Android built-in TTS engine — no heavy dependencies needed
"""

import os
import threading
import time
from pathlib import Path

os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")
os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import get_color_from_hex

# ── Constants ─────────────────────────────────────────────────────────────────

APP_NAME    = "KalamAI"
APP_VERSION = "1.0.0"

# ── Languages ─────────────────────────────────────────────────────────────────

VOICES = {
    "English (US)" : {"locale": "en-US",  "flag": "🇺🇸"},
    "English (UK)" : {"locale": "en-GB",  "flag": "🇬🇧"},
    "Hindi"        : {"locale": "hi-IN",  "flag": "🇮🇳"},
    "Urdu"         : {"locale": "ur-PK",  "flag": "🇵🇰"},
    "Hinglish"     : {"locale": "hi-IN",  "flag": "🇮🇳🇺🇸"},
    "German"       : {"locale": "de-DE",  "flag": "🇩🇪"},
    "French"       : {"locale": "fr-FR",  "flag": "🇫🇷"},
    "Spanish"      : {"locale": "es-ES",  "flag": "🇪🇸"},
    "Portuguese"   : {"locale": "pt-BR",  "flag": "🇧🇷"},
}

# ── KV Layout ─────────────────────────────────────────────────────────────────

KV = """
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<RoundedButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    canvas.before:
        Color:
            rgba: self.bg_color if not self.disabled else get_color_from_hex('#444444')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.radius_val]
    bg_color: get_color_from_hex('#7C3AED')
    radius_val: dp(14)

<RoundedCard@BoxLayout>:
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
    bg_color: get_color_from_hex('#2D2B45')
    padding: dp(16)
    spacing: dp(8)

ScreenManager:
    MainScreen:
        name: 'main'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: app.bg_color
            Rectangle:
                pos: self.pos
                size: self.size

        # ── Header ──────────────────────────────────────────────────────────
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(88)
            padding: dp(18), dp(10)
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#7C3AED')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [0, 0, dp(22), dp(22)]
            BoxLayout:
                orientation: 'horizontal'
                Label:
                    text: '🎙️ KalamAI'
                    font_size: dp(23)
                    bold: True
                    color: 1, 1, 1, 1
                    halign: 'left'
                    text_size: self.size
                    valign: 'center'
                Button:
                    size_hint: None, None
                    size: dp(38), dp(38)
                    background_color: 0, 0, 0, 0
                    background_normal: ''
                    text: '🌙' if app.dark_mode else '☀️'
                    font_size: dp(20)
                    on_release: app.toggle_theme()
            Label:
                text: 'Your Words, Our Voice'
                font_size: dp(11)
                color: 0.85, 0.75, 1, 1
                halign: 'left'
                text_size: self.size
                valign: 'top'
                size_hint_y: None
                height: dp(18)

        # ── Body ────────────────────────────────────────────────────────────
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(14)
                spacing: dp(12)

                # ── Language Selector ────────────────────────────────────────
                RoundedCard:
                    bg_color: app.card_color
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(100)
                    Label:
                        text: '🌍  Select Language'
                        font_size: dp(13)
                        bold: True
                        color: app.text_color
                        halign: 'left'
                        text_size: self.size
                        valign: 'center'
                        size_hint_y: None
                        height: dp(26)
                    ScrollView:
                        do_scroll_y: False
                        do_scroll_x: True
                        size_hint_y: None
                        height: dp(62)
                        BoxLayout:
                            id: lang_box
                            orientation: 'horizontal'
                            size_hint_x: None
                            width: self.minimum_width
                            spacing: dp(8)

                # ── Text Input ───────────────────────────────────────────────
                RoundedCard:
                    bg_color: app.card_color
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(210)
                    Label:
                        text: '✏️  Enter Text'
                        font_size: dp(13)
                        bold: True
                        color: app.text_color
                        halign: 'left'
                        text_size: self.size
                        valign: 'center'
                        size_hint_y: None
                        height: dp(26)
                    TextInput:
                        id: txt_input
                        hint_text: 'Type here... اردو / हिंदी / English'
                        background_color: app.input_bg
                        foreground_color: app.text_color
                        font_size: dp(14)
                        multiline: True
                        padding: dp(10)
                        cursor_color: get_color_from_hex('#7C3AED')
                        size_hint_y: None
                        height: dp(150)
                    BoxLayout:
                        size_hint_y: None
                        height: dp(22)
                        Label:
                            id: char_count
                            text: '0 / 1000'
                            font_size: dp(11)
                            color: app.subtext_color
                            halign: 'right'
                            text_size: self.size
                            valign: 'center'

                # ── Voice Settings ───────────────────────────────────────────
                RoundedCard:
                    bg_color: app.card_color
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(130)

                    Label:
                        text: '⚙️  Voice Settings'
                        font_size: dp(13)
                        bold: True
                        color: app.text_color
                        halign: 'left'
                        text_size: self.size
                        valign: 'center'
                        size_hint_y: None
                        height: dp(26)

                    # Speed
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(36)
                        spacing: dp(8)
                        Label:
                            text: '🐢 Speed'
                            font_size: dp(12)
                            color: app.subtext_color
                            size_hint_x: 0.3
                            halign: 'left'
                            text_size: self.size
                            valign: 'center'
                        Slider:
                            id: speed_slider
                            min: 0.5
                            max: 2.0
                            value: 1.0
                            size_hint_x: 0.5
                            cursor_size: dp(18), dp(18)
                        Label:
                            text: '{:.1f}x'.format(speed_slider.value)
                            font_size: dp(12)
                            color: app.text_color
                            size_hint_x: 0.2
                            halign: 'right'
                            text_size: self.size
                            valign: 'center'

                    # Pitch
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(36)
                        spacing: dp(8)
                        Label:
                            text: '🎵 Pitch'
                            font_size: dp(12)
                            color: app.subtext_color
                            size_hint_x: 0.3
                            halign: 'left'
                            text_size: self.size
                            valign: 'center'
                        Slider:
                            id: pitch_slider
                            min: 0.5
                            max: 2.0
                            value: 1.0
                            size_hint_x: 0.5
                            cursor_size: dp(18), dp(18)
                        Label:
                            text: '{:.1f}x'.format(pitch_slider.value)
                            font_size: dp(12)
                            color: app.text_color
                            size_hint_x: 0.2
                            halign: 'right'
                            text_size: self.size
                            valign: 'center'

                # ── Action Buttons ───────────────────────────────────────────
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(54)
                    spacing: dp(10)

                    RoundedButton:
                        id: btn_speak
                        text: '▶  Speak'
                        font_size: dp(15)
                        bold: True
                        color: 1, 1, 1, 1
                        bg_color: get_color_from_hex('#7C3AED')
                        on_release: app.on_speak()

                    RoundedButton:
                        id: btn_stop
                        text: '⏹  Stop'
                        font_size: dp(15)
                        bold: True
                        color: 1, 1, 1, 1
                        bg_color: get_color_from_hex('#DC2626')
                        disabled: True
                        on_release: app.on_stop()

                    RoundedButton:
                        id: btn_clear
                        text: '🗑  Clear'
                        font_size: dp(15)
                        bold: True
                        color: 1, 1, 1, 1
                        bg_color: get_color_from_hex('#374151')
                        on_release: app.on_clear()

                # ── Status ───────────────────────────────────────────────────
                RoundedCard:
                    bg_color: app.card_color
                    size_hint_y: None
                    height: dp(52)
                    Label:
                        id: status_label
                        text: '🎙️  Ready — Select language and speak!'
                        font_size: dp(12)
                        color: app.subtext_color
                        halign: 'left'
                        text_size: self.size
                        valign: 'center'

                # ── Info Card ────────────────────────────────────────────────
                RoundedCard:
                    bg_color: app.card_color
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(90)
                    Label:
                        text: 'ℹ️  About KalamAI'
                        font_size: dp(12)
                        bold: True
                        color: get_color_from_hex('#A78BFA')
                        halign: 'left'
                        text_size: self.size
                        valign: 'center'
                        size_hint_y: None
                        height: dp(24)
                    Label:
                        text: 'Powered by Android TTS Engine\\n9 Languages • Free Forever • No Ads\\nv1.0.0 — Your Words, Our Voice'
                        font_size: dp(11)
                        color: app.subtext_color
                        halign: 'left'
                        text_size: self.size
                        valign: 'top'

                Widget:
                    size_hint_y: None
                    height: dp(24)
"""


# ── Language Chip ─────────────────────────────────────────────────────────────

class LangChip(BoxLayout):
    selected = BooleanProperty(False)

    def __init__(self, lang_name, flag, on_select_cb, **kwargs):
        super().__init__(**kwargs)
        self.lang_name     = lang_name
        self.on_select_cb  = on_select_cb
        self.orientation   = 'vertical'
        self.size_hint     = (None, None)
        self.size          = (dp(82), dp(58))
        self.padding       = dp(3)

        from kivy.uix.button import Button
        self._btn = Button(
            text=f"{flag}\n{lang_name}",
            font_size=dp(9),
            halign='center',
            valign='center',
            text_size=(dp(82), None),
            background_normal='',
            background_color=(0, 0, 0, 0),
        )
        self._btn.bind(on_release=lambda *_: self.on_select_cb(self.lang_name))
        self.add_widget(self._btn)
        self._refresh()

    def set_selected(self, val):
        self.selected = val
        self._refresh()

    def _refresh(self):
        if self.selected:
            self._btn.background_color = get_color_from_hex('#7C3AED')
            self._btn.color = (1, 1, 1, 1)
            self._btn.bold  = True
        else:
            self._btn.background_color = get_color_from_hex('#3D3B55')
            self._btn.color = get_color_from_hex('#C4B5FD')
            self._btn.bold  = False


# ── Main Screen ───────────────────────────────────────────────────────────────

class MainScreen(Screen):
    pass


# ── App ───────────────────────────────────────────────────────────────────────

class KalamAIApp(App):
    dark_mode     = BooleanProperty(True)
    bg_color      = ListProperty([0.11, 0.11, 0.18, 1])
    card_color    = ListProperty([0.18, 0.17, 0.27, 1])
    text_color    = ListProperty([0.93, 0.91, 1.0,  1])
    subtext_color = ListProperty([0.65, 0.60, 0.80, 1])
    input_bg      = ListProperty([0.14, 0.13, 0.22, 1])

    def __init__(self, **kw):
        super().__init__(**kw)
        self._sel      = "English (US)"
        self._chips    = {}
        self._tts      = None        # Android TTS object
        self._speaking = False

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self):
        self.title = "KalamAI"
        Builder.load_string(KV)
        self._sm = ScreenManager()
        self._sm.add_widget(MainScreen(name='main'))
        return self._sm

    def on_start(self):
        self._init_tts()
        self._build_chips()
        self._bind_counter()
        self._apply_theme()

    # ── Android TTS Init ──────────────────────────────────────────────────────

    def _init_tts(self):
        """Initialize Android TextToSpeech engine."""
        try:
            from jnius import autoclass  # type: ignore
            from android import activity  # type: ignore

            TTS        = autoclass('android.speech.tts.TextToSpeech')
            self._TTS  = TTS
            self._Locale = autoclass('java.util.Locale')

            # TTS init listener
            class TTSListener:
                def onInit(self_inner, status):
                    if status == TTS.SUCCESS:
                        Clock.schedule_once(lambda dt: self._on_tts_ready(), 0)
                    else:
                        Clock.schedule_once(
                            lambda dt: self._status("❌ TTS engine init failed"), 0
                        )

            self._tts = TTS(activity, TTSListener())
            self._status("⏳ Initializing TTS engine…")

        except Exception as e:
            # Desktop fallback — use pyttsx3 if available
            self._tts = None
            self._status(f"ℹ️ Running in preview mode: {e}")

    def _on_tts_ready(self):
        self._status("✅ TTS Ready — Select language and speak!")
        self._set_language(self._sel)

    def _set_language(self, lang_name):
        """Set TTS locale for selected language."""
        if not self._tts:
            return
        try:
            locale_str = VOICES[lang_name]["locale"]
            parts      = locale_str.split("-")
            if len(parts) == 2:
                locale = self._Locale(parts[0], parts[1])
            else:
                locale = self._Locale(parts[0])
            result = self._tts.setLanguage(locale)
            if result < 0:
                self._status(f"⚠️ {lang_name} not supported on this device")
        except Exception as e:
            self._status(f"⚠️ Language error: {e}")

    # ── Chips ─────────────────────────────────────────────────────────────────

    def _build_chips(self):
        lb = self._sm.get_screen('main').ids.lang_box
        lb.clear_widgets()
        self._chips = {}
        for name, info in VOICES.items():
            chip = LangChip(
                lang_name=name,
                flag=info['flag'],
                on_select_cb=self._on_lang,
            )
            if name == self._sel:
                chip.set_selected(True)
            self._chips[name] = chip
            lb.add_widget(chip)
        lb.width = len(VOICES) * (dp(82) + dp(8))

    def _on_lang(self, name):
        self._sel = name
        for n, c in self._chips.items():
            c.set_selected(n == name)
        self._set_language(name)
        self._status(f"{VOICES[name]['flag']}  {name} selected")

    # ── Counter ───────────────────────────────────────────────────────────────

    def _bind_counter(self):
        txt = self._sm.get_screen('main').ids.txt_input
        txt.bind(text=self._on_text_changed)

    def _on_text_changed(self, instance, value):
        ids = self._sm.get_screen('main').ids
        count = len(value)
        ids.char_count.text = f"{count} / 1000"
        ids.char_count.color = (1, 0.3, 0.3, 1) if count > 1000 else self.subtext_color

    # ── Theme ─────────────────────────────────────────────────────────────────

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_theme()

    def _apply_theme(self):
        if self.dark_mode:
            self.bg_color      = [0.11, 0.11, 0.18, 1]
            self.card_color    = [0.18, 0.17, 0.27, 1]
            self.text_color    = [0.93, 0.91, 1.0,  1]
            self.subtext_color = [0.65, 0.60, 0.80, 1]
            self.input_bg      = [0.14, 0.13, 0.22, 1]
        else:
            self.bg_color      = [0.96, 0.95, 1.0,  1]
            self.card_color    = [1.0,  1.0,  1.0,  1]
            self.text_color    = [0.12, 0.11, 0.30, 1]
            self.subtext_color = [0.35, 0.30, 0.55, 1]
            self.input_bg      = [0.95, 0.94, 1.0,  1]
        for c in self._chips.values():
            c._refresh()

    # ── Speak ─────────────────────────────────────────────────────────────────

    def on_speak(self):
        ids  = self._sm.get_screen('main').ids
        text = ids.txt_input.text.strip()

        if not text:
            self._status("⚠️  Please enter some text first!")
            return
        if len(text) > 1000:
            self._status("⚠️  Max 1000 characters!")
            return

        speed = ids.speed_slider.value
        pitch = ids.pitch_slider.value

        if self._tts:
            self._speak_android(text, speed, pitch, ids)
        else:
            self._speak_fallback(text, ids)

    def _speak_android(self, text, speed, pitch, ids):
        """Use Android TTS to speak."""
        try:
            from jnius import autoclass  # type: ignore
            Bundle = autoclass('android.os.Bundle')

            self._tts.setSpeechRate(speed)
            self._tts.setPitch(pitch)

            # Android API 21+ uses speak() with QUEUE_FLUSH
            self._tts.speak(text, self._TTS.QUEUE_FLUSH, None, "KalamAI_utterance")

            self._speaking = True
            ids.btn_speak.disabled = True
            ids.btn_stop.disabled  = False
            self._status("🔊  Speaking…")

            # Poll for completion
            Clock.schedule_interval(lambda dt: self._check_done(ids), 0.5)

        except Exception as e:
            self._status(f"❌  TTS error: {e}")

    def _check_done(self, ids):
        """Check if TTS finished speaking."""
        try:
            if not self._tts.isSpeaking():
                self._speaking = False
                self._reset_buttons(ids)
                self._status("✅  Done!")
                return False   # Stop polling
        except Exception:
            return False
        return True  # Keep polling

    def _speak_fallback(self, text, ids):
        """Desktop fallback using pyttsx3."""
        try:
            import pyttsx3  # type: ignore
            def _run():
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                Clock.schedule_once(lambda dt: self._reset_buttons(ids), 0)
                self._status("✅  Done!")
            threading.Thread(target=_run, daemon=True).start()
            self._status("🔊  Speaking (preview mode)…")
            ids.btn_speak.disabled = True
            ids.btn_stop.disabled  = False
        except Exception as e:
            self._status(f"❌  Fallback TTS error: {e}")

    # ── Stop ──────────────────────────────────────────────────────────────────

    def on_stop(self):
        try:
            if self._tts:
                self._tts.stop()
        except Exception:
            pass
        self._speaking = False
        ids = self._sm.get_screen('main').ids
        self._reset_buttons(ids)
        self._status("⏹  Stopped.")

    # ── Clear ─────────────────────────────────────────────────────────────────

    def on_clear(self):
        ids = self._sm.get_screen('main').ids
        ids.txt_input.text = ""
        self._status("🗑  Text cleared.")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @mainthread
    def _reset_buttons(self, ids):
        ids.btn_speak.disabled = False
        ids.btn_stop.disabled  = True

    @mainthread
    def _status(self, msg):
        try:
            self._sm.get_screen('main').ids.status_label.text = msg
        except Exception:
            pass

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def on_stop_app(self):
        try:
            if self._tts:
                self._tts.stop()
                self._tts.shutdown()
        except Exception:
            pass


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    KalamAIApp().run()
