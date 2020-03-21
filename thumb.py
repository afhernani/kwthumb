# ! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import threading
import errno
import time
from utility import items_only_a 
import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import sp
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.settings import SettingsWithSidebar, ConfigParser
from settingsjson import settings_json
from movie import Movie

class ButtonThumb(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(ButtonThumb, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            print("double_tap") 
            return True
        else:
            print("single_tap")
            # return True
        return super().on_touch_down(touch)

class Thumb(BoxLayout):
    def __init__(self, source, **kwargs):
        super(Thumb, self).__init__(**kwargs)
        # si existe el fichero lo adicionamos, si no, 
        # no lo adicionamos.
        if os.path.exists(source):
            self.ids.imgview.source=source
            self.ids.label.text = source

    def addate_image(self, th):
        print('action_image:', th.encode('utf-8'))


class ThumbView(BoxLayout):
    stop = threading.Event()
    files=[]
    def __init__(self, files=[], **kwargs):
        super().__init__(**kwargs)
        self.files=files
        for file in self.files:
            self.ids.box.add_widget(Thumb(source=file))
        for key, value in kwargs.items():
            if key=='source':
                self.files.append(value)


class Mensaje(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.font_size = sp(20)

    def on_size(self, *args):
        self.text_size = (self.width-sp(10), None)

    def on_texture_size(self, *args):
        self.size = self.texture_size
        self.height += sp(20)


class ThumbApp(App):
    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        self.root.stop.set()

    def build(self):
        '''constructor de la aplicacion '''
        self.settings_cls = SettingsWithSidebar
        self.files=[]
        # files = ['bbt.gif', 'huge.gif', 'kingy-anal.gif', 'mellons.gif', 'mother.gif']
        ''' lee un registro configuración de la app '''
        self.directorio  = self.config.get('example', 'pathexample')
        # directorio = 'F:\\tmp\\VSDG_E'
        # directorio = 'F:\\tmp\\_Clasic_moom'
        # self.thumbview = ThumbView(files=files)
        self.thumbview = ThumbView()
        self.load_thread(self.directorio)
        return self.thumbview
    
    def build_config(self, config):
        ''' establece configuracion por defecto de la app, si no existe el fichero
        settings.ini, lo crea y adiciona los valores por defecto '''
        config.setdefaults('example', {
            'boolexample': True,
            'numericexample': 10,
            'optionsexample': 'option2',
            'stringexample':'some_string',
            'pathexample':'f:/tmp/VSDG_E'
        })
        # self.config = config

    def build_settings(self, settings):
        ''' inserta al panel de configuración de kivy la configuracion de la aplicacion '''
        settings.add_json_panel('Thumb', self.config, data=settings_json)

    def on_config_change(self, config, section, 
                         key, value):
        ''' se ejecuta cuando cambia los valores del panel settings '''
        print(config, section, key, value)

    def change_value(self, section, key, value):
        ''' establecemos un valor pathexample nuevo en la seccion example '''
        # self.config.set('example','pathexample','f:/tmp/kvsettings')
        self.config.set(section, key, value)
        print('change_value: ', section, key, value)

    def load_thread(self, dirpath='.'):
        from functools import partial
        self.dirpathmovies = dirpath
        self.title='Splitfloat :: ' + self.dirpathmovies
        self.thumbview.ids.idpath.text = self.dirpathmovies
        # print('dirpathmovies:', self.dirpathmovies)
        exten = ('.gif', '.GIF')
        dirthumbs = os.path.join(self.dirpathmovies, 'Thumbails')
        # print('dirthumbs:', dirthumbs)
        self.thumbview.ids.box.clear_widgets()
        self.files=[]
        if os.path.exists(dirthumbs):
            for fe in os.listdir(dirthumbs):
                if fe.endswith(exten):
                    fex = os.path.abspath(os.path.join(dirthumbs, fe))
                    # print(fex.encode('utf-8'))
                    self.files.append(fex)
                    # Clock.schedule_once(partial(self.update_box_imagen, str(fex)))
                    # self.box.ids.box.add_widget(Splitfloat(source=fex, anim_delay= 1))
        self.title += ' ' + str(len(self.files))
        self.thumbview.ids._status_bar.ids.label_a.text = 'Total Thumbs: '+ str(len(self.files))
        Clock.schedule_once(self.thread_load_files)
        # threading.Thread(target=self.start_load_thread, args=(self.files,), daemon=False).start()
        #print('files:', self.files,', len:', len(self.files))

    def thread_load_files(self, *args):
        threading.Thread(target=self.start_load_thread, args=(self.files,), daemon=False).start()

    def start_load_thread(self, files=[]):
        try:
            for file in files:
                self.update_box_imagen(file)
            self.disable_button()
        except:
            print('excepcion en start_load_thread')
        
    @mainthread
    def disable_button(self, *args):
        if self.thumbview.ids.btnaplicar.disabled == True:
            self.thumbview.ids.btnaplicar.disabled = False
        if self.thumbview.general_option.ids.btnmake.disabled == True:
            self.thumbview.general_option.ids.btnmake.disabled = False
        if self.thumbview.general_option.ids.btncancel.disabled == True:
            self.thumbview.general_option.ids.btncancel.disabled = False

    @mainthread
    def update_box_imagen(self, file ):
        self.thumbview.ids.box.add_widget(Thumb(source=file))
        self.thumbview.ids.imgview.source = file

    def aplicar(self, instance, *args):
        print('aplicar:', args)
        print('instance:', instance)
        print(f'state: {instance.state}')
        instance.disabled = True
        print(f'state: {instance.state}')
        dirmovies = self.thumbview.ids.idpath.text
        if os.path.isdir(dirmovies):
            print(f'exist directory: {dirmovies}')
            dirmoviesthumbs = os.path.join(dirmovies, 'Thumbails')
            if os.path.isdir(dirmoviesthumbs):
                print(f'exist directory: {dirmoviesthumbs}')
            else:
                try:
                    os.mkdir(dirmoviesthumbs, 0o666)
                    print(f'make directory: {dirmoviesthumbs}')
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
            if self.directorio != dirmovies:
                print(f'anterior: {self.directorio}, adiconado: {dirmovies}')
                self.directorio = dirmovies
                self.load_thread(self.directorio)
                self.config.set('example','pathexample', str(self.directorio))
                self.config.write()
            else:
                instance.disabled = False
        else:
            print(f'do not exist directory: {dirmovies}')
            self.thumbview.ids.idpath.text = self.dirpathmovies
            instance.disabled = False
            return 0

    def on_analisis(self, instance, *args):
        print('on_analisis: ', args)
        instance.disabled = True
        c, f = items_only_a(self.dirpathmovies)
        print(f'c -> {c}; total: {len(c)}')
        print(f'f -> {f}; total: {len(f)}')
        self.thumbview.ids._status_bar.ids.label_b.text = 'Kivy pending thumb: '+ str(len(c))
        instance.disabled = False

    def on_make(self, instance, *args):
        instance.disabled = True
        self.list_base, self.list_thumbs = items_only_a(self.dirpathmovies)
        self.thumbview.ids._status_bar.ids.label_b.text =f'on_make: files gif {str(len(self.list_base))}'
        # self.list_base, están los ficheros de video que no tienen gif y vamos a crearlos
        threading.Thread(target=self.thread_make_gifs, args=(self.list_base, self.dirpathmovies, ), daemon=True).start()

    CANCEL = False # cancelar la orden de tarea.

    def thread_make_gifs(self, list_base=[], path='.'):
        try:
            pendient= len(list_base)
            for item in list_base:
                if not self.CANCEL:
                    file =os.path.join(path, item)
                    giffile = os.path.join(path, 'Thumbails', item + '_thumbs_0000.gif')
                    print(f'>>> thread_make_gifs, n:{pendient}, {file}, {giffile}')
                    movie = Movie(file)
                    movie.run()
                    while movie.isAlive():
                        pass
                    self.update_box_imagen(giffile)
                    pendient -= 1
                    self.update_mensaje_label_b(str(pendient))
                else:
                    self.CANCEL = False
                    self.disable_button()
                    return
            self.disable_button()
        except OSError as e:
            print(e.message)
        except e:
            print(e.message)
            self.thumbview.ids._status_bar.ids.label_b.text =f'on_make: except'
            self.disable_button()

    def on_cancel(self, instance):
        instance.disabled = True
        self.CANCEL = True 

    @mainthread
    def update_mensaje_label_b(self, info='' ):
        self.thumbview.ids._status_bar.ids.label_b.text =f'on_make: files gif {info}'

if __name__ == '__main__':
    ThumbApp().run()