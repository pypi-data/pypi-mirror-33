
from . import glmath, scenes
from . import widgets as wid
from . import gl as mygl
from .plot import PlotTab
import copy
from .widgets import ArrangeV, ArrangeH
from .thread import inthread, inmain_decorator
from qtconsole.inprocess import QtInProcessRichJupyterWidget
from .config import icon_path
import numpy as np

import time
from ngsolve.bla import Vector
from math import exp, sqrt

from PySide2 import QtWidgets, QtOpenGL, QtCore, QtGui
from OpenGL import GL
import pickle


class ToolBoxItem(QtWidgets.QWidget):
    def __init__(self, window, scene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QtWidgets.QVBoxLayout()
        for item in scene.widgets.groups:
            layout.addWidget(item)
        self.setLayout(layout)
        self.layout().setAlignment(QtCore.Qt.AlignTop)
        self.scene = scene
        self.window = window

    def changeActive(self):
        self.scene.active = not self.scene.active
        self.window.glWidget.updateGL()

    def mousePressEvent(self, event):
        drag = QtGui.QDrag(self)
        mime_data = QtCore.QMimeData()
        dump = pickle.dumps(self.scene)
        mime_data.setData("scene", dump)
        drag.setMimeData(mime_data)
        drag.start()

class SceneToolBox(QtWidgets.QToolBox):
    ic_visible = icon_path + "/visible.png"
    ic_hidden = icon_path + "/hidden.png"
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.scenes = []

    def addScene(self, scene):
        self.scenes.append(scene)
        icon = QtGui.QIcon(SceneToolBox.ic_visible if scene.active else SceneToolBox.ic_hidden)
        widget = ToolBoxItem(self.window,scene)
        self.setCurrentIndex(self.addItem(widget,icon, scene.name))

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            event.accept()
            clicked = self.childAt(event.pos())
            i = 0
            index = None
            while self.layout().itemAt(i) is not None:
                if self.layout().itemAt(i).widget() == clicked:
                    index = i//2
                i += 1
            if index is not None:
                widget = self.widget(index)
                widget.changeActive()
                if widget.scene.active:
                    self.setCurrentIndex(index)
                self.setItemIcon(index, QtGui.QIcon(SceneToolBox.ic_visible if
                                                    widget.scene.active else SceneToolBox.ic_hidden))
        if event.buttons() == QtCore.Qt.MidButton:
            event.accept()
            clicked = self.childAt(event.pos())
            i = 0
            index = None
            while self.layout().itemAt(i) is not None:
                if self.layout().itemAt(i).widget() == clicked:
                    index = i//2
                i += 1
            if index is not None:
                scene = self.scenes[index]
                self.scenes.remove(scene)
                self.removeItem(index)
                self.window.glWidget.scenes.remove(scene)
                self.window.glWidget.updateGL()

class RenderingParameters:
    def __init__(self):
        self.rotmat = glmath.Identity()
        self.zoom = 0.0
        self.ratio = 1.0
        self.dx = 0.0
        self.dy = 0.0
        self.min = Vector(3)
        self.min[:] = 0.0
        self.max = Vector(3)
        self.max[:] = 0.0

        self.clipping_rotmat = glmath.Identity()
        self.clipping_normal = Vector(4)
        self.clipping_normal[0] = 1.0
        self.clipping_point = Vector(3)
        self.clipping_dist = 0.0

        self.colormap_min = 0
        self.colormap_max = 1
        self.colormap_linear = False

        self.fastmode = False

    def __getstate__(self):
        return (np.array(self.rotmat), self.zoom, self.ratio, self.dx, self.dy, np.array(self.min),
                np.array(self.max), np.array(self.clipping_rotmat), np.array(self.clipping_normal),
                np.array(self.clipping_point), self.clipping_dist, self.colormap_min, self.colormap_max,
                self.colormap_linear, self.fastmode)

    def __setstate__(self,state):
        self.__init__()
        rotmat, self.zoom, self.ratio, self.dx, self.dy, _min, _max, cl_rotmat, cl_normal, cl_point, self.clipping_dist, self.colormap_min, self.colormap_max, self.colormap_linear, self.fastmode = state
        for i in range(4):
            for j in range(4):
                self.rotmat[i,j] = rotmat[i,j]
                self.clipping_rotmat[i,j] = cl_rotmat[i,j]
            self.clipping_normal[i] = cl_normal[i]
        for i in range(3):
            self.min[i] = _min[i]
            self.max[i] = _max[i]
            self.clipping_point[i] = cl_point[i]

    @property
    def center(self):
        return 0.5*(self.min+self.max)

    @property
    def _modelSize(self):
        return sqrt(sum((self.max[i]-self.min[i])**2 for i in range(3)))

    @property
    def model(self):
        mat = glmath.Identity();
        mat = self.rotmat*mat;
        mat = glmath.Scale(2./self._modelSize) * mat
        mat = glmath.Translate(self.dx, -self.dy, -0 )*mat;
        mat = glmath.Scale(exp(-self.zoom/100))*mat;
        mat = glmath.Translate(0, -0, -5 )*mat;
        mat = mat*glmath.Translate(-self.center[0], -self.center[1], -self.center[2]) #move to center
        return mat

    @property
    def view(self):
        return glmath.LookAt()

    @property
    def projection(self):
        return glmath.Perspective(0.8, self.ratio, .1, 20.)

    @property
    def clipping_plane(self):
        x = self.clipping_rotmat * self.clipping_normal
        d = glmath.Dot(self.clipping_point,x[0:3])
        x[3] = -d
        x[3] = x[3]-self.clipping_dist
        return x

    def getClippingPlaneNormal(self):
        x = self.clipping_rotmat * self.clipping_normal
        return x[0:3]

    def getClippingPlanePoint(self):
        return self.clipping_point

    def setClippingPlaneNormal(self, normal):
        for i in range(3):
            self.clipping_normal[i] = normal[i]
        self.clipping_rotmat = glmath.Identity()

    def setClippingPlanePoint(self, point):
        for i in range(3):
            self.clipping_point[i] = point[i]

class WindowTab(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._startup_scenes = []

    def create(self,sharedContext):
        self.glWidget = GLWidget(shared=sharedContext)
        self.glWidget.makeCurrent()

        buttons = QtWidgets.QVBoxLayout()

        btnZoomReset = QtWidgets.QPushButton("ZoomReset", self)
        btnZoomReset.clicked.connect(self.glWidget.ZoomReset)
        btnZoomReset.setMinimumWidth(1);

        buttons.addWidget(btnZoomReset)

        self.toolbox = SceneToolBox(self)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.glWidget)
        tbwidget = QtWidgets.QWidget()
        tbwidget.setLayout(ArrangeV(self.toolbox, buttons))
        splitter.addWidget(tbwidget)
        splitter.setOrientation(QtCore.Qt.Horizontal)
        splitter.setSizes([75000, 25000])
        self.setLayout(ArrangeH(splitter))
        self.overlay = scenes.OverlayScene(name="Global options",
                                           rendering_parameters=self.glWidget._rendering_parameters)
        self.draw(self.overlay)
        for scene in self._startup_scenes:
            if isinstance(scene, scenes.OverlayScene):
                self.overlay.copyOptionsFrom(scene)
            else:
                self.draw(scene)

    def __getstate__(self):
        return (self.glWidget.scenes,)

    def __setstate__(self,state):
        self.__init__()
        self._startup_scenes = state[0]

    def isGLWindow(self):
        return True

    @inmain_decorator(True)
    def draw(self, scene):
        self.glWidget.makeCurrent()
        scene.window = self
        scene.update()
        self.glWidget.addScene(scene)
        self.toolbox.addScene(scene)


class GLWidget(QtOpenGL.QGLWidget):
    redraw_signal = QtCore.Signal()

    def __init__(self,shared=None, *args, **kwargs):
        f = QtOpenGL.QGLFormat()
        f.setVersion(3,2)
        f.setProfile(QtOpenGL.QGLFormat.CompatibilityProfile)
        QtOpenGL.QGLFormat.setDefaultFormat(f)
        super().__init__(shareWidget=shared, *args, **kwargs)
        if shared is None:
            self.context().setFormat(f)
            self.context().create()
        self.scenes = []
        self._rotation_enabled = True
        self.do_rotate = False
        self.do_translate = False
        self.do_zoom = False
        self.do_move_clippingplane = False
        self.do_rotate_clippingplane = False
        self.old_time = time.time()
        self._rendering_parameters = RenderingParameters()

        self.redraw_update_done = QtCore.QWaitCondition()
        self.redraw_mutex = QtCore.QMutex()

        self.redraw_signal.connect(self.updateScenes)

        self.lastPos = QtCore.QPoint()
        self.lastFastmode = self._rendering_parameters.fastmode

    @inmain_decorator(True)
    def updateGL(self,*args,**kwargs):
        super().updateGL(*args,**kwargs)

    def ZoomReset(self):
        self._rendering_parameters.rotmat = glmath.Identity()
        self._rendering_parameters.zoom = 0.0
        self._rendering_parameters.dx = 0.0
        self._rendering_parameters.dy = 0.0
        self.updateGL()

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def initializeGL(self):
        self.updateScenes()

    def updateScenes(self):
        self.redraw_mutex.lock()
        self.makeCurrent()
        for scene in self.scenes:
            if scene.active:
                scene.update()
        self.redraw_update_done.wakeAll()
        self.redraw_mutex.unlock()
        self.update()

    def paintGL(self):
        t = time.time() - self.old_time
#         print("frames per second: ", 1.0/t, end='\r')
        self.old_time = time.time()


        GL.glClearColor( 1, 1, 1, 0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glEnable(GL.GL_BLEND);
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

        viewport = GL.glGetIntegerv( GL.GL_VIEWPORT )
        screen_width = viewport[2]-viewport[0]
        screen_height = viewport[3]-viewport[1]
        with mygl.Query(GL.GL_PRIMITIVES_GENERATED) as q:
            rp = copy.copy(self._rendering_parameters)
            rp.ratio = screen_width/max(screen_height,1)
            for scene in self.scenes:
                scene.render(rp) #model, view, projection)
        # print('\rtotal trigs drawn ' + str(q.value)+' '*10, end='')

    def addScene(self, scene):
        self.scenes.append(scene)
        self.scenes.sort(key=lambda x: x.deferRendering())
        box_min = Vector(3)
        box_max = Vector(3)
        box_min[:] = 1e99
        box_max[:] = -1e99
        for scene in self.scenes:
            if not scene.active:
                continue
            s_min, s_max = scene.getBoundingBox()
            for i in range(3):
                box_min[i] = min(s_min[i], box_min[i])
                box_max[i] = max(s_max[i], box_max[i])
        self._rendering_parameters.min = box_min
        self._rendering_parameters.max = box_max
        self.updateGL()

    def mouseDoubleClickEvent(self, event):
        import OpenGL.GLU
        viewport = GL.glGetIntegerv( GL.GL_VIEWPORT )
        x = event.pos().x()
        y = viewport[3]-event.pos().y()
        GL.glReadBuffer(GL.GL_FRONT);
        z = GL.glReadPixels(x, y, 1, 1, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT)
        params = self._rendering_parameters
        p = OpenGL.GLU.gluUnProject(
                x,y,z,
                (params.view*params.model).T.NumPy(),
                params.projection.T.NumPy(),
                viewport,
                )
        for scene in self.scenes:
            scene.doubleClickAction(p)


########################
# font
#         painter = QtGui.QPainter(self)
#         painter.drawLine(0, 0, 1, 1);
#         painter.end()

# ########################
#         GL.glUseProgram(0)
#         GL.glDisable(GL.GL_DEPTH_TEST)
#         GL.glMatrixMode(GL.GL_PROJECTION)
#         GL.glOrtho( -.5, .5, .5, -.5, -1000, 1000)
#         GL.glMatrixMode(GL.GL_MODELVIEW)
#         GL.glLoadIdentity()
# #         GL.glClearColor(1.0, 1.0, 1.0, 1.0)
#
#
#         GL.glClear(GL.GL_COLOR_BUFFER_BIT)
#
#         self.qglColor(QtCore.Qt.black)
#         self.renderText(0.0, 0.0, 0.0, "Multisampling enabled")
# #         self.renderText(0.15, 0.4, 0.0, "Multisampling disabled")
########################

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        self._rendering_parameters.ratio = width/max(1,height)

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())
        self.lastFastmode = self._rendering_parameters.fastmode
        self._rendering_parameters.fastmode = True
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.button() == QtCore.Qt.MouseButton.RightButton:
                self.do_move_clippingplane = True
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.do_rotate_clippingplane = True
        else:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                if self._rotation_enabled:
                    self.do_rotate = True
            if event.button() == QtCore.Qt.MouseButton.MidButton:
                self.do_translate = True
            if event.button() == QtCore.Qt.MouseButton.RightButton:
                self.do_zoom = True

    def mouseReleaseEvent(self, event):
        self.do_rotate = False
        self.do_translate = False
        self.do_zoom = False
        self.do_move_clippingplane = False
        self.do_rotate_clippingplane = False
        if self._rendering_parameters.fastmode and not self.lastFastmode:
            self._rendering_parameters.fastmode = False
            self.updateGL()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        param = self._rendering_parameters
        if self.do_rotate:
            param.rotmat = glmath.RotateY(-dx/50.0)*param.rotmat
            param.rotmat = glmath.RotateX(-dy/50.0)*param.rotmat
        if self.do_translate:
            s = 200.0*exp(-param.zoom/100)
            param.dx += dx/s
            param.dy += dy/s
        if self.do_zoom:
            param.zoom += dy
        if self.do_move_clippingplane:
            s = 200.0*exp(-param.zoom/100)
            shift = -dy/s*param.getClippingPlaneNormal()
            p = param.getClippingPlanePoint()
            param.setClippingPlanePoint(p+shift)
        if self.do_rotate_clippingplane:
            # rotation of clipping plane is view-dependent
            r = param.rotmat
            param.clipping_rotmat = r.T*glmath.RotateY(-dx/50.0)*r*param.clipping_rotmat
            param.clipping_rotmat = r.T*glmath.RotateX(-dy/50.0)*r*param.clipping_rotmat
        self.lastPos = QtCore.QPoint(event.pos())
        self.updateGL()

    def wheelEvent(self, event):
        self._rendering_parameters.zoom -= event.angleDelta().y()/10
        self.updateGL()

    def freeResources(self):
        self.makeCurrent()

class WindowTabBar(QtWidgets.QTabBar):
    def __init__(self, tabber, *args,**kwargs):
        super().__init__(*args,**kwargs)
        self.tabber = tabber
        self.setAcceptDrops(True)

    def dragEnterEvent(self,event):
        if event.mimeData().hasFormat("scene"):
            event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("scene"):
            index = self.tabAt(event.pos())
            self.tabber.setCurrentIndex(index)
            self.tabber.activeGLWindow = self.tabber.currentWidget()
            event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("scene"):
            scene = self.tabber.draw(pickle.loads(event.mimeData().data("scene").data()))
            event.accept()

class WindowTabber(QtWidgets.QTabWidget):
    def __init__(self,commonContext, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self._commonContext = commonContext
        self.setTabBar(WindowTabBar(self))
        self.setTabsClosable(True)
        self._activeGLWindow = None
        self.tabCloseRequested.connect(self._remove_tab)
        self._fastmode = False

    def _getActiveGLWindow(self):
        if not self._activeGLWindow:
            self.make_window()
        return self._activeGLWindow
    def _setActiveGLWindow(self, win):
        self.setCurrentWidget(win)
        self._activeGLWindow = win
    activeGLWindow = property(_getActiveGLWindow, _setActiveGLWindow)

    @inmain_decorator(True)
    def _remove_tab(self, index):
        if self.widget(index).isGLWindow():
            if self.activeGLWindow == self.widget(index):
                self.activeGLWindow = None
                for i in range(self.count()):
                    if isinstance(self.widget(self.count()-i-1), WindowTab):
                        self.activeGLWindow = self.widget(self.count()-i-1)
                        break
            self.removeTab(index)

    def draw(self, *args, tab=None, **kwargs):
        if tab is not None:
            tab_found = False
            for i in range(self.count()):
                if self.tabText(i) == tab:
                    # tab already exists -> activate it
                    tab_found = True
                    self.activeGLWindow = self.widget(i)
            if not tab_found:
                # create new tab with given name
                self.make_window(name=tab)
        self.activeGLWindow.draw(*args,**kwargs)

    @inmain_decorator(True)
    def plot(self, x, y):
        window = PlotTab()
        window.plot(x,y)
        self.addTab(window, "plot")
        self.setCurrentWidget(window)

    def setCurrentIndex(self, index):
        super().setCurrentIndex(index)
        if isinstance(self.currentWidget(), WindowTab):
            self.activeGLWindow = self.currentWidget()

    @inmain_decorator(True)
    def make_window(self, name=None):
        window = WindowTab()
        window.create(sharedContext=self._commonContext)
        if self._fastmode:
            window.glWidget._rendering_parameters.fastmode = True
        name = name or "window" + str(self.count() + 1)
        self.addTab(window, name)
        self.activeGLWindow = window
