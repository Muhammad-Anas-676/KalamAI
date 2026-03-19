"""
KalamAI - "Your Words, Our Voice"
Multilingual TTS App powered by Piper
v1.0.0
"""
import os, sys, json, wave, threading, time
from pathlib import Path

os.environ.setdefault("KIVY_NO_ENV_CONFIG","1")
os.environ.setdefault("KIVY_NO_CONSOLELOG","1")

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import get_color_from_hex

APP_NAME    = "KalamAI"
APP_TAGLINE = "Your Words, Our Voice"
APP_VERSION = "1.0.0"

COLOR_PRIMARY       = "#7C3AED"
COLOR_PRIMARY_DARK  = "#5B21B6"
COLOR_PRIMARY_LIGHT = "#A78BFA"
COLOR_SURFACE_DARK  = "#1C1B2E"
COLOR_SURFACE_LIGHT = "#F5F3FF"
COLOR_CARD_DARK     = "#2D2B45"
COLOR_CARD_LIGHT    = "#FFFFFF"
COLOR_TEXT_DARK     = "#EDE9FE"
COLOR_TEXT_LIGHT    = "#1E1B4B"

VOICES = {
  "English (US)": {"code":"en_US","model":"en_US-lessac-medium.onnx","url":"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx","url_json":"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json","flag":"🇺🇸","size":"63 MB"},
  "English (UK)": {"code":"en_GB","model":"en_GB-alba-medium.onnx","url":"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx","url_json":"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx.json","flag":"🇬🇧","size":"63 MB"},
  "Hindi":        {"code":"hi_IN","model":"hi_IN-dhruva-medium.onnx","url":"https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/dhruva/medium/hi_IN-dhruva-medium.onnx","url_json":"https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/dhruva/medium/hi_IN-dhruva-medium.onnx.json","flag":"🇮🇳","size":"63 MB"},
  "German":       {"code":"de_DE","model":"de_DE-thorsten-medium.onnx","url":"https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx","url_json":"https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json","flag":"🇩🇪","size":"63 MB"},
  "French":       {"code":"fr_FR","model":"fr_FR-upmc-medium.onnx","url":"https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx","url_json":"https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json","flag":"🇫🇷","size":"63 MB"},
  "Spanish":      {"code":"es_ES","model":"es_ES-davefx-medium.onnx","url":"https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx","url_json":"https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json","flag":"🇪🇸","size":"63 MB"},
  "Portuguese":   {"code":"pt_BR","model":"pt_BR-faber-medium.onnx","url":"https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx","url_json":"https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json","flag":"🇧🇷","size":"63 MB"},
  "Hinglish":     {"code":"hinglish","model":"en_US-lessac-medium.onnx","url":"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx","url_json":"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json","flag":"🇮🇳","size":"63 MB"},
  "Urdu":         {"code":"urdu","model":"hi_IN-dhruva-medium.onnx","url":"https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/dhruva/medium/hi_IN-dhruva-medium.onnx","url_json":"https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/dhruva/medium/hi_IN-dhruva-medium.onnx.json","flag":"🇵🇰","size":"63 MB"},
}

KV = """
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex
<RoundedButton@Button>:
    background_color: 0,0,0,0
    background_normal: ''
    canvas.before:
        Color:
            rgba: self.bg_color if not self.disabled else get_color_from_hex('#555555')
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
    spacing: dp(10)
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
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(90)
            padding: dp(20), dp(12)
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#7C3AED')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [0, 0, dp(24), dp(24)]
            BoxLayout:
                orientation: 'horizontal'
                Label:
                    text: '🎙️ KalamAI'
                    font_size: dp(24)
                    bold: True
                    color: 1,1,1,1
                    halign: 'left'
                    text_size: self.size
                    valign: 'center'
                Button:
                    size_hint: None, None
                    size: dp(36), dp(36)
                    background_color: 0,0,0,0
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
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16)
                spacing: dp(14)
                RoundedCard:
                    bg_color: app.card_color
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(100)
                    Label:
                        text: '🌍 Select Language'
                        font_size: dp(13)
                        bold: True
                        color: app.text_color
                        halign: 'left'
                        text_size: self.size
                        valign: 'center'
                        size_hint_y: None
                        height: dp(28)
                    ScrollView:
                        do_scroll_y: False
                        do_scroll_x: True
                        BoxLayout:
                            id: lang_box
                            orientation: 'horizontal'
                            size_hint_x: None
                            width: self.minimum_width
                            spacing: dp(8)
                RoundedCard:
                    bg_color: app.card_color
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(200)
                    Label:
                        text: '✏️ Enter Text'
                        font_size: dp(13)
                        bold: True
                        color: app.text_color
                        halign: 'left'
                        text_size: self.size
                        valign: 'center'
                        size_hint_y: None
                        height: dp(28)
                    TextInput:
                        id: txt_input
                        hint_text: 'Type text here... Urdu/Hindi/English'
                        background_color: app.input_bg
                        foreground_color: app.text_color
                        font_size: dp(14)
                        multiline: True
                        padding: dp(10)
                        size_hint_y: None
                        height: dp(140)
                    BoxLayout:
                        size_hint_y: None
                        height: dp(24)
                        Label:
                            id: char_count
                            text: '0 / 500'
                            font_size: dp(11)
                            color: app.subtext_color
                            halign: 'right'
                            text_size: self.size
                            valign: 'center'
                RoundedCard:
                    bg_color: app.card_color
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(80)
                    Label:
                        text: '⚙️ Speed'
                        font_size: dp(12)
                        color: app.text_color
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: dp(24)
                    Slider:
                        id: speed_slider
                        min: 0.5
                        max: 2.0
                        value: 1.0
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(56)
                    spacing: dp(10)
                    RoundedButton:
                        id: btn_speak
                        text: '▶  Speak'
                        font_size: dp(15)
                        bold: True
                        color: 1,1,1,1
                        bg_color: get_color_from_hex('#7C3AED')
                        on_release: app.on_speak()
                    RoundedButton:
                        id: btn_stop
                        text: '⏹  Stop'
                        font_size: dp(15)
                        bold: True
                        color: 1,1,1,1
                        bg_color: get_color_from_hex('#DC2626')
                        disabled: True
                        on_release: app.on_stop_audio()
                    RoundedButton:
                        id: btn_save
                        text: '💾  Save'
                        font_size: dp(15)
                        bold: True
                        color: 1,1,1,1
                        bg_color: get_color_from_hex('#059669')
                        disabled: True
                        on_release: app.on_save()
                RoundedCard:
                    bg_color: app.card_color
                    size_hint_y: None
                    height: dp(54)
                    Label:
                        id: status_label
                        text: '🎙️ Ready — Select language and type text'
                        font_size: dp(12)
                        color: app.subtext_color
                        halign: 'left'
                        text_size: self.size
                        valign: 'center'
                Widget:
                    size_hint_y: None
                    height: dp(20)
"""

class LangChip(BoxLayout):
    selected = BooleanProperty(False)
    def __init__(self, lang_name, flag, on_select_cb, **kwargs):
        super().__init__(**kwargs)
        self.lang_name=lang_name; self.flag=flag; self.on_select_cb=on_select_cb
        self.orientation='vertical'; self.size_hint=(None,None); self.size=(dp(80),dp(60)); self.padding=dp(4)
        from kivy.uix.button import Button
        self._btn=Button(text=f"{flag}\n{lang_name}",font_size=dp(10),halign='center',valign='center',text_size=(dp(80),None),background_normal='',background_color=(0,0,0,0))
        self._btn.bind(on_release=lambda *_:self.on_select_cb(self.lang_name))
        self.add_widget(self._btn); self._refresh()
    def set_selected(self,v):
        self.selected=v; self._refresh()
    def _refresh(self):
        if self.selected: self._btn.background_color=get_color_from_hex('#7C3AED'); self._btn.color=(1,1,1,1); self._btn.bold=True
        else: self._btn.background_color=get_color_from_hex('#3D3B55'); self._btn.color=get_color_from_hex('#C4B5FD'); self._btn.bold=False

class MainScreen(Screen): pass

class KalamAIApp(App):
    dark_mode=BooleanProperty(True)
    bg_color=ListProperty([0.11,0.11,0.18,1])
    card_color=ListProperty([0.18,0.17,0.27,1])
    text_color=ListProperty([0.93,0.91,1.0,1])
    subtext_color=ListProperty([0.65,0.60,0.80,1])
    input_bg=ListProperty([0.14,0.13,0.22,1])

    def __init__(self,**kw):
        super().__init__(**kw)
        self._sel='English (US)'; self._chips={}; self._audio=None; self._wav=''; self._speaking=False; self._vdir=Path('')

    def build(self):
        self.title='KalamAI'; Builder.load_string(KV)
        self._sm=ScreenManager(); self._sm.add_widget(MainScreen(name='main')); return self._sm

    def on_start(self):
        self._setup_dirs(); self._build_chips(); self._bind_counter(); self._apply_theme()

    def _setup_dirs(self):
        base = Path(os.environ.get('ANDROID_APP_PATH', str(Path.home()/'.kalamAI')))
        self._vdir=(base/'voices'); self._vdir.mkdir(parents=True,exist_ok=True)

    def _build_chips(self):
        lb=self._sm.get_screen('main').ids.lang_box; lb.clear_widgets(); self._chips={}
        for n,info in VOICES.items():
            c=LangChip(lang_name=n,flag=info['flag'],on_select_cb=self._on_lang)
            if n==self._sel: c.set_selected(True)
            self._chips[n]=c; lb.add_widget(c)
        lb.width=len(VOICES)*(dp(80)+dp(8))

    def _bind_counter(self):
        self._sm.get_screen('main').ids.txt_input.bind(text=lambda i,v:setattr(self._sm.get_screen('main').ids.char_count,'text',f'{len(v)} / 500'))

    def toggle_theme(self):
        self.dark_mode=not self.dark_mode; self._apply_theme()

    def _apply_theme(self):
        if self.dark_mode:
            self.bg_color=[0.11,0.11,0.18,1]; self.card_color=[0.18,0.17,0.27,1]; self.text_color=[0.93,0.91,1.0,1]; self.subtext_color=[0.65,0.60,0.80,1]; self.input_bg=[0.14,0.13,0.22,1]
        else:
            self.bg_color=[0.96,0.95,1.0,1]; self.card_color=[1,1,1,1]; self.text_color=[0.12,0.11,0.30,1]; self.subtext_color=[0.35,0.30,0.55,1]; self.input_bg=[0.96,0.95,1.0,1]
        for c in self._chips.values(): c._refresh()

    def _on_lang(self,name):
        self._sel=name
        for n,c in self._chips.items(): c.set_selected(n==name)
        self._status(f"{VOICES[name]['flag']} {name} selected")

    def on_speak(self):
        ids=self._sm.get_screen('main').ids; text=ids.txt_input.text.strip()
        if not text: self._status('⚠️ Please enter text first.'); return
        if len(text)>500: self._status('⚠️ Max 500 characters!'); return
        vi=VOICES[self._sel]; mp=self._vdir/vi['model']
        if not mp.exists(): self._download_then_speak(vi,mp,text,ids)
        else: self._synth(text,mp,ids)

    def _download_then_speak(self,vi,mp,text,ids):
        self._status(f"⬇️ Downloading {self._sel} ({vi['size']})…")
        def _dl():
            try:
                import urllib.request
                json_p=self._vdir/(vi['model']+'.json')
                urllib.request.urlretrieve(vi['url_json'],json_p)
                urllib.request.urlretrieve(vi['url'],mp)
                Clock.schedule_once(lambda dt:self._synth(text,mp,ids),0)
            except Exception as e:
                Clock.schedule_once(lambda dt:self._status(f'❌ Download failed: {e}'),0)
        threading.Thread(target=_dl,daemon=True).start()

    def _synth(self,text,mp,ids):
        self._status('🔄 Synthesizing…'); ids.btn_speak.disabled=True; ids.btn_stop.disabled=False
        sp=self._sm.get_screen('main').ids.speed_slider.value
        def _s():
            try:
                from piper.voice import PiperVoice
                op=self._vdir/'output.wav'
                v=PiperVoice.load(str(mp),config_path=str(mp)+'.json',use_cuda=False)
                with wave.open(str(op),'wb') as wf: v.synthesize(text,wf,length_scale=1.0/sp)
                self._wav=str(op)
                Clock.schedule_once(lambda dt:self._play(str(op),ids),0)
            except Exception as e:
                Clock.schedule_once(lambda dt:self._err(str(e),ids),0)
        threading.Thread(target=_s,daemon=True).start()

    @mainthread
    def _play(self,path,ids):
        s=SoundLoader.load(path)
        if s:
            self._audio=s; self._speaking=True
            s.bind(on_stop=lambda *_:Clock.schedule_once(lambda dt:self._reset(ids),0))
            s.play(); self._status('🔊 Playing…'); ids.btn_save.disabled=False
        else: self._status('❌ Audio load failed'); self._reset(ids)

    @mainthread
    def _err(self,e,ids): self._status(f'❌ {e}'); self._reset(ids)

    def on_stop_audio(self):
        if self._audio: self._audio.stop()
        self._speaking=False; ids=self._sm.get_screen('main').ids; self._reset(ids); self._status('⏹ Stopped.')

    @mainthread
    def _reset(self,ids): ids.btn_speak.disabled=False; ids.btn_stop.disabled=True

    def on_save(self):
        if not self._wav: return
        try:
            from android.storage import primary_external_storage_path
            ext=primary_external_storage_path()
        except: ext=str(Path.home())
        sd=Path(ext)/'KalamAI'; sd.mkdir(parents=True,exist_ok=True)
        import shutil; fn=f'kalamAI_{int(time.time())}.wav'; shutil.copy2(self._wav,sd/fn)
        self._status(f'💾 Saved: KalamAI/{fn}')

    @mainthread
    def _status(self,msg):
        try: self._sm.get_screen('main').ids.status_label.text=msg
        except: pass

if __name__=='__main__': KalamAIApp().run()
