# ! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import threading
import errno
import time
from utility import items_only_a, lunch_video, lunch_video_default
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
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import sp
from kivy.uix.image import Image
from kivy.graphics import Line, Rectangle, Color
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.settings import SettingsWithSidebar, ConfigParser
from settingsjson import settings_json
from movie import Movie
from kivy.uix.videoplayer import VideoPlayer
try:
    from kivy.garden.xpopup.tools import *
    from kivy.garden.xpopup.file import XFolder
except ImportError as error:
    print('you might install librery kivy.garden.xpopup', str(error.args))

__author__='hernani'
__email__ = 'afhernani@gmail.com'
__apply__ = 'thumb app for gif and viedo viewer'
__version__ = 0.1

class ButtonThumb(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(ButtonThumb, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        
        if self.collide_point(touch.x, touch.y):
            if touch.is_double_tap:
                print(f"double_tap: {self.source}")
                lunch_video_default(self.source)
                self.touched = True
                return True
            self.touched = True
            #return True
        return super(ButtonThumb, self).on_touch_down(touch)


class Thumb(BoxLayout):
    def __init__(self, source, **kwargs):
        super(Thumb, self).__init__(**kwargs)
        self.selected = None
        # si existe el fichero lo adicionamos, si no, 
        # no lo adicionamos.
        if os.path.exists(source):
            self.ids.imgview.source=source
            self.ids.label.text = source

    def addate_image(self, th):
        print('action_image:', th.encode('utf-8'))

    def on_touch_down(self, touch):
        
        if self.collide_point(touch.x, touch.y):
            if self.btntoggle.state == 'down':
                if not self.selected:
                    self.select()
                else:
                    self.unselect()
            self.touched = True
            #return True
        return super(Thumb, self).on_touch_down(touch)

    def select(self):
        print('select()', self.top)
        if not self.selected:
            # self.ix, self.iy = self.to_widget(self.x, self.y)
            # self.ix = self.center_x
            # self.iy = self.center_y
            with self.canvas:
                Color(.234, .456, .678, .4)
                self.selected = Rectangle(pos = self.pos, 
                                          size =(self.width, 
                                              self.height ), 
                                          dash_offset=2, color=(1,1,1), width=10)
            # Update the canvas as the screen size change 
            self.bind(pos = self.update_rect,)

    def update_rect(self, *args):
        self.selected.pos = self.pos

    def unselect(self):
        print('unselect()')
        if self.selected:
            self.unbind(pos=self.update_rect,)
            self.canvas.remove(self.selected)
            # self.remove(self.selected)
            self.selected = None


class ThumbView(BoxLayout):
    stop = threading.Event()
    def __init__(self, files=[], **kwargs):
        super().__init__(**kwargs)
        self.m_video = VideoPlayer(source='video/wot-tanks.mp4', state='play', 
                                 options={'allow_stretch': True, 'eos': 'loop'} )
        self.ids.boxvideo.add_widget(self.m_video)
        self.files=files
        for file in self.files:
            self.ids.box.add_widget(Thumb(source=file))
        for key, value in kwargs.items():
            if key=='source':
                self.files.append(value)

    def change_video(self, instancia):
        print('change_video')
        _video_name = os.path.basename(instancia).split("_thumbs_")[0]
        _dirname = instancia.split('Thumbails')[0]
        _video = os.path.join(_dirname,  _video_name)
        if os.path.exists(_video):
            self.m_video.source= _video
        else:
            print('file not found:', _video)

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

# from kivy.config import Config
from kivy.core.window import Window

class ThumbApp(App):
    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        ''' se dispara el evento al iniciarse la detencion de la aplicacion '''
        print('on_stop: ')
        self.root.stop.set()

    def on_start(self, **kvargs):
        ''' lunch after build and start window '''
        Window.bind(on_resize=self.on_resize)
        # Window.bind(on_motion=self.on_motion_thumbapp)
        # Window.bind(on_draw=self.on_draw_thumbapp)
        Window.bind(on_request_close=self.on_request_close)
        # self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        Window.bind(on_keyboard=self.on_keyboard)
        # print('on_start')
        w, h, t, l = self.get_sizewindow(self.config.get('example','sizewindow'))
        # print(w, h, t, l)
        Window.size = (int(w), int(h))
        Window.Top = int(t)
        Window.left = int(l)

    def on_keyboard(self, keyboard, key, text, modifiers, *args):
        print(f'{keyboard}, {key}, {text}, {modifiers}, {args}')
        return True

    def on_request_close(self, *args):
        self.textpopup(title='Exit', text='Are you sure?')
        return True

    def textpopup(self, title='', text=''):
        """Open the pop-up with the name.
 
        :param title: title of the pop-up to open
        :type title: str
        :param text: main text of the pop-up to open
        :type text: str
        :rtype: None
        """
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=text))
        mybutton = Button(text='OK', size_hint=(1, 0.25))
        box.add_widget(mybutton)
        popup = Popup(title=title, content=box, size_hint=(None, None), size=(300, 200))
        mybutton.bind(on_release=self.stop) # manda detener la aplicación
        popup.open()

    def on_motion(self, window, etype, me):
        ''' arrastrando el raton
        Parameters:	
            window: instancie window
            etype: str 
                One of ‘begin’, ‘update’, ‘end’ 
            me: MotionEvent    
                The Motion Event currently dispatched.
         '''
        # print(f'on_motion_thumbapp: {window}, {etype}, {me}')
        pass
    
    def on_draw(self, window, *args):
        ''' draw window 
            Parmeters:
                window: instance window.
                *args:
        '''
        # print('on_draw_thumbapp: ', window, args)
        pass

    def build(self):
        '''constructor de la aplicacion '''
        self.settings_cls = SettingsWithSidebar
        self.files=[]
        self.total = 0
        # files = ['bbt.gif', 'huge.gif', 'kingy-anal.gif', 'mellons.gif', 'mother.gif']
        ''' lee un registro configuración de la app '''
        self.directorio  = self.config.get('example', 'pathexample')
        # print(self.config.get('example','sizewindow'))
        # directorio = 'F:\\tmp\\VSDG_E'
        # directorio = 'F:\\tmp\\_Clasic_moom'
        # self.thumbview = ThumbView(files=files)
        self.thumbview = ThumbView()
        self.load_thread(self.directorio)
        return self.thumbview
    
    def on_resize(self, instancie, width, height):
        '''Event called when the window is resized'''
        print(f'window.size {str(width)}, {str(height)}')
        print(f'instancie: {instancie.top}, {instancie.left}')
        variable = str(width)+'x'+ str(height) + 'x' + str(instancie.top) + 'x' + str(instancie.left)
        print('variable: '+ variable)
        self.config.set('example', 'sizewindow', variable)
        self.config.write()
        '''
        Config.set('graphics', 'resizable', 1)
        Config.set('graphics', 'position', 'custom')
        Config.set('graphics', 'widht', str(width))
        Config.set('graphics', 'height', str(height))
        Config.set('graphics', 'top', str(instancie.top))
        Config.set('graphics', 'left', str(instancie.left))
        Config.write() '''

    def get_sizewindow(self, cadena):
        return cadena.split('x')

    def build_config(self, config):
        ''' establece configuracion por defecto de la app, si no existe el fichero
        settings.ini, lo crea y adiciona los valores por defecto '''
        config.setdefaults('example', {
            'boolexample': True,
            'numericexample': 10,
            'optionsexample': 'option2',
            'stringexample':'some_string',
            'sizewindow' : '500x900x100x100',
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
        self.total = 0
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
        from time import sleep
        try:
            for file in files:
                self.update_box_imagen(file)
                sleep(0.5)
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
        # self.thumbview.ids.imgview.source = file
        self.total += 1
        self.thumbview.ids._status_bar.ids.label_a.text = 'Total Thumbs: ' + str(self.total) + '/' + str(len(self.files))

    def _folder_dialog(self, instance, *args):
        road = self.thumbview.ids.idpath.text
        # print('_folder_dialog:', road)
        if os.path.exists(road):
            Factory.XFolder(on_dismiss=self._filepopup_callback, path=road)
        else:
            road = os.path.abspath(__file__)
            Factory.XFolder(on_dismiss=self._filepopup_callback, path=road)

    def _filepopup_callback(self, instance, *args):
        # print('_filepopup_callback', instance, instance.path)
        # print('_filepopup_callback', instance.__class__.__name__)
        if instance.is_canceled():
            return
        if instance.__class__.__name__ == 'XFolder':
            self._folder(instance.path)
            # print('ooohh')
        
    def _folder(self, path, *args):
        # print('_folder', path)
        self.thumbview.ids.idpath.text = path
        instance = self.thumbview.ids.btnaplicar
        self.aplicar(instance)
        # print('_folder', instance)

    def on_enter(self,instance, value):
        print(f'on _enter: instance: {instance}, value: {value}')
        instance_btnaplicar = self.thumbview.ids.btnaplicar
        self.aplicar(instance_btnaplicar)
        # return super(TextInput,self).insert_text(substring, from_undo=from_undo)

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
            print(e.args)
        except Exception as e:
            print(e.args)
            self.thumbview.ids._status_bar.ids.label_b.text =f'on_make: except: {e.args}'
            self.disable_button()

    def on_cancel(self, instance):
        instance.disabled = True
        self.CANCEL = True 

    @mainthread
    def update_mensaje_label_b(self, info='' ):
        self.thumbview.ids._status_bar.ids.label_b.text =f'make files gif: {info}'

    def on_btn_open(self, instance):
        boxes = self.thumbview.ids.box
        childrens= boxes.children[:]
        selected =[]
        for child in childrens:
            if child.selected:
                selected.append(child.ids.imgview.source)
                child.unselect()
            # print(child.ids.imgview.source, child.__class__.__name__)
        for item in selected:
            print('selected ->>', item)


if __name__ == '__main__':
    ThumbApp().run()