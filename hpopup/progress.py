
from os.path import join
from kivy import metrics, kivy_data_dir
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import (ListProperty, StringProperty, NumericProperty,
    BoundedNumericProperty, BooleanProperty)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.logger import Logger
try:
    from .hbase import HBase 
    from .notifybase import NotifyBase
except:
    from hbase import HBase 
    from notifybase import NotifyBase

__author__ = 'ophermit, Hernai'

__all__ = ('Progress', 'Loading')

class Progress(NotifyBase):
    """Progress class. See module documentation for more information.
    """

    buttons = ListProperty([NotifyBase.BUTTON_CANCEL])
    '''Default button set for class
    '''

    max = NumericProperty(100.)
    value = NumericProperty(0.)
    '''Properties that are binded to the same ProgressBar properties.
    '''

    def __init__(self, **kwargs):
        self._complete = False
        self._progress = ProgressBar(max=self.max, value=self.value)
        self.bind(max=self._progress.setter('max'))
        self.bind(value=self._progress.setter('value'))
        super(Progress, self).__init__(**kwargs)

    def _get_body(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(super(Progress, self)._get_body())
        layout.add_widget(self._progress)
        return layout

    def complete(self, text='Complete', show_time=2):
        """
        Sets the progress to 100%, hides the button(s) and automatically
        closes the popup.

        .. versionchanged:: 0.2.1
        Added parameters 'text' and 'show_time'

        :param text: text instead of 'Complete', optional
        :param show_time: time-to-close (in seconds), optional
        """
        self._complete = True
        n = self.max
        self.value = n
        self.text = text
        self.buttons = []
        Clock.schedule_once(self.dismiss, show_time)

    def inc(self, pn_delta=1):
        """
        Increase current progress by specified number of units.
         If the result value exceeds the maximum value, this method is
         "looping" the progress

        :param pn_delta: number of units
        """
        self.value += pn_delta
        if self.value > self.max:
            # create "loop"
            self.value = self.value % self.max

    def autoprogress(self, pdt=None):
        """
        .. versionadded:: 0.2.1

        Starts infinite progress increase in the separate thread
        """
        if self._window and not self._complete:
            self.inc()
            Clock.schedule_once(self.autoprogress, .01)


class Loading(HBase):
    """Loading class. See module documentation for more information.

    .. versionadded:: 0.3.0
    """
    gif = StringProperty(join(kivy_data_dir, 'images', 'image-loading.gif'))
    '''Represents a path to an image.
    '''

    title = StringProperty(u'Loading...')
    '''Default title for class
    '''

    size_hint_x = NumericProperty(None, allownone=True)
    size_hint_y = NumericProperty(None, allownone=True)
    width = NumericProperty(metrics.dp(350))
    height = NumericProperty(metrics.dp(200))
    '''Default size properties for the popup
    '''

    def _get_body(self):
        return Image(source=self.gif, anim_delay=.1)



#### comprobaciones. #######################

from os.path import expanduser
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class TestApp(App):
    def build(self):
        label = BoxLayout()
        label.add_widget(Button(text='Progress', on_release=self.btnProgress))
        label.add_widget(Button(text='Loading', on_release=self.btnLoading))
        return label

    def btnProgress(self, *args):
        self._o_popup = Progress(title='PopupProgress demo',
                                text='Processing...', max=200)
        Clock.schedule_once(self._progress_test, .1)

    def _progress_test(self, pdt=None):
        if self._o_popup.is_canceled():
            return

        self._o_popup.inc()
        self._o_popup.text = 'Processing (%d / %d)' %\
                             (self._o_popup.value, self._o_popup.max)
        if self._o_popup.value < self._o_popup.max:
            Clock.schedule_once(self._progress_test, .01)
        else:
            self._o_popup.complete()

    def btnLoading(self, *agrs):
        Loading(buttons=['Close'], on_dismiss=self.my_callback)

    def my_callback(self, instance):
        if instance.is_canceled():
            return

        s_message = 'Pressed button: %s\n\n' % instance.button_pressed

        try:
            values = instance.values
            for kw in values:
                s_message += ('<' + kw + '> : ' + str(values[kw]) + '\n')
        except AttributeError:
            pass

        Logger.info(msg=s_message)


if __name__ == '__main__':
    TestApp().run()