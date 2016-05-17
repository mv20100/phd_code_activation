# -*- coding: utf-8 -*-
# Copyright 2013-2015 Nate Bogdanowicz
"""
Driver for Thorlabs DCx cameras. May be compatible with iDS cameras that use
uEye software. Currently Windows-only, but Linux support should be
possible to implement if desired.
"""

import logging as log
from ctypes import CDLL, WinDLL, byref, pointer, POINTER, c_char, c_char_p, c_wchar_p, cast
from ctypes.wintypes import DWORD, INT, ULONG, DOUBLE, HWND
import os.path
import numpy as np
from _uc480.constants import *
from _uc480.structs import *
from uc480_tools import aviCapture
from uc480_tools_h import *

HCAM = DWORD
NULL = POINTER(HWND)()

import platform
if platform.architecture()[0].startswith('64'):
    lib = WinDLL('uc480_64')
else:
    lib = CDLL('uc480')

def errcheck(res, func, args):
    if res != IS_SUCCESS:
        if func == lib.is_SetColorMode and args[1] == IS_GET_COLOR_MODE:
            pass
        else:
            raise Exception("uEye Error: {}".format(ERR_CODE_NAME[res]))
    return res
lib.is_InitCamera.errcheck = errcheck
lib.is_GetImageMemPitch.errcheck = errcheck
lib.is_SetColorMode.errcheck = errcheck

class UC480_Camera(object):
    """A uc480-supported Camera."""

    def __init__(self, id=1):

        self._id = id
        self._in_use = False
        self._width, self._height = INT(), INT()
        self._color_depth = INT()
        self._color_mode = INT()
        self._list_p_img_mem = None
        self._list_memid = None
        self.is_live = False
        self.is_recording = False

        self._open()

        self.cap = aviCapture(self._hcam)

    def __del__(self):
        if self._in_use:
            self.close()  # In case someone forgot to close()

    def set_auto_exposure(self, enable=True):
        """Enable or disable the auto exposure shutter."""
        ret = lib.is_SetAutoParameter(self._hcam, IS_SET_ENABLE_AUTO_SHUTTER,
                                      pointer(INT(enable)), NULL)
        if ret != IS_SUCCESS:
            print("Failed to set auto exposure property")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _open(self, num_bufs=1):
        """
        Connect to the camera and set up the image memory.
        """
        self._hcam = HCAM(self._id)
        ret = lib.is_InitCamera(byref(self._hcam), NULL)
        if ret != IS_SUCCESS:
            print("Failed to open camera")
        else:
            self._in_use = True
            self.width, self.height = self._get_max_img_size()
            log.debug('image width=%d, height=%d', self.width, self.height)

            self._init_colormode()
            self._allocate_mem_seq(num_bufs)

    def _init_colormode(self):
        log.debug("Initializing default color mode")
        sensor_mode = self._get_sensor_color_mode()
        mode_map = {
            IS_COLORMODE_MONOCHROME: (IS_CM_MONO8, 8),
            IS_COLORMODE_BAYER: (IS_CM_RGBA8_PACKED, 32)
        }
        try:
            mode, depth = mode_map[sensor_mode]
        except KeyError:
            raise Exception("Currently unsupported sensor color mode!")

        self._color_mode, self._color_depth = DWORD(mode), DWORD(depth)
        log.debug('color_depth=%d, color_mode=%d', depth, mode)

        lib.is_SetColorMode(self._hcam, self._color_mode)

    def _free_image_mem_seq(self):
        lib.is_ClearSequence(self._hcam)
        for p_img_mem, memid in zip(self._list_p_img_mem, self._list_memid):
            lib.is_FreeImageMem(self._hcam, p_img_Mem, memid)
        self._list_p_img_mem = None
        self._list_memid = None

    def _allocate_mem_seq(self, num_bufs):
        """
        Create and setup the image memory for live capture
        """
        self._list_p_img_mem = []
        self._list_memid = []
        for i in range(num_bufs):
            p_img_mem = POINTER(c_char)()
            memid = INT()
            lib.is_AllocImageMem(self._hcam, self._width, self._height, self._color_depth,
                                 pointer(p_img_mem), pointer(memid))
            lib.is_AddToSequence(self._hcam, p_img_mem, memid)
            self._list_p_img_mem.append(p_img_mem)
            self._list_memid.append(memid)

        # Initialize display
        lib.is_SetImageSize(self._hcam, self._width, self._height)
        lib.is_SetDisplayMode(self._hcam, IS_SET_DM_DIB)

    def _install_event_handler(self):
        try:
            import win32event
        except ImportError:
            raise ImportError("Live video events require the win32event module")
        self.hEvent = win32event.CreateEvent(None, False, False, '')
        lib.is_InitEvent(self._hcam, self.hEvent.handle, IS_SET_EVENT_FRAME)
        lib.is_EnableEvent(self._hcam, IS_SET_EVENT_FRAME)

    def _uninstall_event_handler(self):
        lib.is_DisableEvent(self._hcam, IS_SET_EVENT_FRAME)
        lib.is_ExitEvent(self._hcam, IS_SET_EVENT_FRAME)

    def close(self):
        """Close the camera and release associated image memory.

        Should be called when you are done using the camera. Alternatively, you
        can use the camera as a context manager--see the documentation for
        __init__.
        """
        ret = lib.is_ExitCamera(self._hcam)
        if ret != IS_SUCCESS:
            print("Failed to close camera")
        else:
            self._in_use = False
            print("Camera closed")

    def _bytes_per_line(self):
        num = INT()
        ret = lib.is_GetImageMemPitch(self._hcam, pointer(num))
        if ret == IS_SUCCESS:
            log.debug('bytes_per_line=%d', num.value)
            return num.value
        raise Exception("Return code {}".format(ret))

    def wait_for_frame(self, timeout=0):
        """ Wait for FRAME event to be signaled. 
            
            Parameters
            ----------
            timeout : int, optional
                How long to wait for event to be signaled. If timeout is 0,
                this polls the event status and reterns immediately.

            Returns
            -------
            bool
                Whether FRAME event was signaled.
        """
        try:
            import win32event
        except ImportError:
            raise ImportError("Live video events require the win32event module")
        ret = win32event.WaitForSingleObject(self.hEvent, timeout)
        return (ret == win32event.WAIT_OBJECT_0)

    def freeze_frame(self):
        """Acquire an image from the camera and store it in memory.

        Can be used in conjunction with direct memory access to display an
        image without saving it to file.
        """
        ret = lib.is_FreezeVideo(self._hcam, self._width, self._height)
        log.debug("FreezeVideo retval=%d", ret)

    def start_live_video(self, framerate=None):
        """Start live video capture.
        
        Parameters
        ----------
        framerate : float, optional
            Desired framerate. The true framerate that results can be found in
            the ``framerate`` attribute.
        """
        self._install_event_handler()
        if framerate is None:
            framerate = IS_GET_FRAMERATE
        newFPS = DOUBLE()
        ret = lib.is_SetFrameRate(self._hcam, DOUBLE(framerate), pointer(newFPS))
        if ret != IS_SUCCESS:
            print("Error: failed to set framerate")
        else:
            self.framerate = newFPS.value
        print("Framerate: {}".format(self.framerate))
        lib.is_CaptureVideo(self._hcam, IS_WAIT)
        self.is_live = True

    def start_recording(self,filename="test.avi"):
        if self.is_live:
            self.cap.OpenAVI(filename)
            self.cap.SetImageSize(IS_AVI_CM_RGB32,self.width,self.height,0,0,0)
            self.cap.SetImageQuality(100)
            self.cap.SetFrameRate(self.framerate)
            self.cap.StartAVI()
            self.is_recording = True

    def stop_recording(self):
        self.is_recording = False
        self.cap.StopAVI()
        self.cap.CloseAVI()

    def stop_live_video(self):
        """Stop live video capture."""
        lib.is_StopLiveVideo(self._hcam, IS_WAIT)
        self._uninstall_event_handler()
        self.is_live = False

    def save_image(self, filename=None, filetype=None, freeze=None):
        """Save the current video image to disk.

        If no filename is given, this will display the 'Save as' dialog. If no
        filetype is given, it will be determined by the extension of the
        filename, if available.  If neither exists, the image will be saved as
        a bitmap (BMP) file.

        Parameters
        ----------
        filename : str, optional
            Filename to save image as. If not given, 'Save as' dialog will open.
        filetype : str, optional
            Filetype to save image as, e.g. 'bmp'. Useful for setting the
            default filetype in the 'Save as' dialog.
        freeze : bool, optional
            Freeze a frame before copying data. By default, freezes when not in
            live capture mode.
        """
        if freeze is None:
            freeze = not self.is_live

        # Strip extension from filename, clear extension if it is invalid
        if filename is not None:
            filename, ext = os.path.splitext(filename)
            if ext.lower() not in ['.bmp', '.jpg', '.png']:
                ext = '.bmp'
        else:
            filename, ext = '', '.bmp'

        # 'filetype' flag overrides the extension. Default is .bmp
        if filetype:
            ext = '.' + filetype.lower()

        fdict = {'.bmp': IS_IMG_BMP, '.jpg': IS_IMG_JPG, '.png': IS_IMG_PNG}
        ftype_flag = fdict[ext.lower()]
        filename = filename + ext if filename else None

        if freeze:
            lib.is_FreezeVideo(self._hcam, self._width, self._height)
        lib.is_SaveImageEx(self._hcam, filename, ftype_flag, INT(0))

    def _get_max_img_size(self):
        # TODO: Make this more robust
        sInfo = SENSORINFO()
        lib.is_GetSensorInfo(self._hcam, byref(sInfo))
        return sInfo.nMaxWidth, sInfo.nMaxHeight

    def _get_sensor_color_mode(self):
        sInfo = SENSORINFO()
        lib.is_GetSensorInfo(self._hcam, byref(sInfo))
        return int(sInfo.nColorMode.encode('hex'), 16)

    def _value_getter(member_str):
        def getter(self):
            return getattr(self, member_str).value
        return getter

    def _value_setter(member_str):
        def setter(self, value):
            getattr(self, member_str).value = value
        return setter

    def image_array(self, freeze=True):
        """ Get an array of the data in the active image memory.

        The array's shape depends on the camera's color mode. Monochrome modes
        return an array with shape (height, width), while camera modes return
        an array with shape (height, width, 3) where the last axis contains the
        RGB channels in that order.

        This format is useful for sending to matplotlib's ``imshow()``
        function::

            >>> ...
            >>> import matplotlib.pyplot as plt
            >>> cam.freeze_frame()
            >>> plt.imshow(cam.image_array())
            >>> plt.show()

        Parameters
        ----------
        freeze : bool, optional
            Freeze a frame before copying data. By default, freezes when not in
            live capture mode.
        """
        # Currently only supports MONO8 and RGBA8_PACKED
        if (not self.is_live if freeze is None else freeze):
            lib.is_FreezeVideo(self._hcam, self._width, self._height)

        h = self.height
        buf = self.image_buffer()
        self.arr = np.frombuffer(buf, np.uint8)

        if self._color_mode.value == IS_CM_RGBA8_PACKED:
            w = self.bytes_per_line/4
            self.arr = self.arr.reshape((h,w,4), order='C')
        elif self._color_mode.value == IS_CM_BGRA8_PACKED:
            w = self.bytes_per_line/4
            self.arr = self.arr.reshape((h,w,4), order='C')[:,:,2::-1]
        elif self._color_mode.value == IS_CM_MONO8:
            w = self.bytes_per_line
            self.arr = self.arr.reshape((h,w), order='C')
        else:
            raise Exception("Unsupported color mode!")
        return self.arr

    def image_buffer(self):
        """ Get a buffer of the active image memory's bytes. """
        bpl = self.bytes_per_line

        # Create a pointer to the data as a CHAR ARRAY so we can convert it to a buffer
        p_img_mem = self._last_img_mem()
        arr_ptr = cast(p_img_mem, POINTER(c_char * (bpl*self.height)))
        if self.is_recording:
            print self.cap.AddFrame(arr_ptr)
        return buffer(arr_ptr.contents)  # buffer pointing to array of image data

    def _last_img_mem(self):
        """ Returns a ctypes char-pointer to the starting address of the image memory
        last used for image capturing """
        nNum = INT()
        pcMem = POINTER(c_char)()
        pcMemLast = POINTER(c_char)()
        lib.is_GetActSeqBuf(self._hcam, pointer(nNum), pointer(pcMem), pointer(pcMemLast))
        return pcMemLast

    def _color_mode_string(self):
        MAP = {
            IS_CM_MONO8: 'mono8',
            IS_CM_MONO16: 'mono16',
        }
        return MAP.get(self._color_mode.value)

    #: uEye camera ID number. Read-only
    id = property(lambda self: self._id)

    #: Camera model number string. Read-only
    model = property(lambda self: self._model)

    #: Number of bytes used by each line of the image. Read-only
    bytes_per_line = property(lambda self: self._bytes_per_line())

    #: Width of the camera image in pixels
    width = property(_value_getter('_width'), _value_setter('_width'))

    #: Height of the camera image in pixels
    height = property(_value_getter('_height'), _value_setter('_height'))

    #: Color mode string. Read-only
    color_mode = property(lambda self: self._color_mode_string())


if __name__ == '__main__':
    cam = UC480_Camera(id=1)
