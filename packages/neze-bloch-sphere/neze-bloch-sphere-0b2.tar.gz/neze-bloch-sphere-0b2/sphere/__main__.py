from logging import getLogger,ERROR,DEBUG,basicConfig
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch,Circle
from mpl_toolkits.mplot3d import proj3d
from matplotlib.widgets import Slider,RadioButtons
from collections import OrderedDict as odict

basicConfig()
logger = getLogger(__name__)
logger.setLevel(ERROR)

class Arrow3D(FancyArrowPatch):
    prop = dict(mutation_scale=20, arrowstyle='-|>', color='k', shrinkA=0, shrinkB=0)
    def __init__(self, xs, ys, zs, *args, **kwargs):
        prop = dict(self.prop)
        prop.update(kwargs)
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **prop)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)

    def update(self,x,y,z):
        self._verts3d[0][1] = x
        self._verts3d[1][1] = y
        self._verts3d[2][1] = z

class Arrow(FancyArrowPatch):
    prop = dict(mutation_scale=20, arrowstyle='-|>', color='k', shrinkA=0, shrinkB=0)
    def __init__(self,x,y,*args,**kwargs):
        prop = dict(self.prop)
        prop.update(kwargs)
        FancyArrowPatch.__init__(self,(0,0),(0,0),*args,**prop)
        self._verts = x,y
    def draw(self,renderer):
        x,y = self._verts
        self.set_positions((0,0),(x,y))
        FancyArrowPatch.draw(self,renderer)
    def update(self,x,y):
        self._verts = x,y

class MyArrayClass(np.ndarray):
    KET = 0b10
    BRA = 0b11^KET
    BRAKET = BRA|KET
    KETBRA = BRA&KET

    def __new__(cls, array):
        logger.debug('In __new__:{:}'.format(cls))
        return np.array(array).view(cls)
    def __init__(self,*args,**kwargs):
        logger.debug('In __init__:{:}'.format(self.__class__))
    def __array_finalize__(self,obj):
        logger.debug('In __array_finalize__:{:} -> {:}'.format(type(obj),type(self)))
        s = self.shape
        if len(s)!=2:
            raise TypeError

    def tc(self):
        return self.transpose().conjugate()
    @property
    def type(self):
        try:
            t = self.__type
        except AttributeError:
            t = None
        if t is None:
            s = self.shape
            self.__type = 1*(s[0]==1)+2*(s[1]==1)
        return self.__type

    __mul__ = np.ndarray.dot

    @property
    def x(self):
        if self.type in [self.KET,self.BRA]:
            return self.view(np.ndarray)[0][0]
        raise TypeError
    @property
    def y(self):
        if self.type in [self.KET,self.BRA]:
            return self.view(np.ndarray)[1*bool(self.type&self.KET)][1*bool(self.type&self.BRA)]
        raise TypeError
    @property
    def xx(self):
        if self.type == self.KETBRA:
            return self.view(np.ndarray)[0][0]
        raise TypeError
    @property
    def yy(self):
        if self.type == self.KETBRA:
            return self.view(np.ndarray)[1][1]
        raise TypeError
    @property
    def xy(self):
        if self.type == self.KETBRA:
            return self.view(np.ndarray)[0][1]
        raise TypeError
    @property
    def yx(self):
        if self.type == self.KETBRA:
            return self.view(np.ndarray)[1][0]
        raise TypeError

    def ket(self):
        if self.type == self.KET:
            return self
        if self.type == self.BRA:
            return self.tc()
        raise TypeError
    def bra(self):
        if self.type == self.BRA:
            return self
        if self.type == self.KET:
            return self.tc()
        raise TypeError
    def norm(self):
        if self.type == self.BRAKET:
            return self.view(np.ndarray)[0][0]
        if self.type in [self.BRA,self.KET]:
            return (self.bra()*self.ket()).norm()
        if self.type == self.KETBRA:
            v = self.view(np.ndarray)
            return v[0][0]+v[1][1]
        raise TypeError
    def dm(self):
        n = self.norm()
        if self.type in [self.BRA,self.KET]:
            return (1./n)*(self.ket()*self.bra())
        if self.type == self.KETBRA:
            return (1./n)*self
        raise TypeError

    def coord(self):
        dm = self.dm()
        x,y,z = (dm.xy+dm.yx).real,(1j*(dm.xy-dm.yx)).real,(dm.xx-dm.yy).real
        # print((x*x+y*y+z*z))
        return x,y,z

Ket0 = MyArrayClass(np.array([1,0]).reshape(-1,1))
Ket1 = MyArrayClass(np.array([0,1]).reshape(-1,1))
Bra0 = MyArrayClass(np.array([1,0]).reshape(1,-1))

def GateX(a):# GateX for angle 2aπ
    alpha = a*np.pi # half-angle
    c = np.cos(alpha)
    s = -1j*np.sin(alpha)
    return MyArrayClass(np.array([[c,s],[s,c]]))
def GateY(a):# GateY for angle 2aπ
    alpha = a*np.pi # half-angle
    c = np.cos(alpha)
    s = np.sin(alpha)
    return MyArrayClass(np.array([[c,-s],[s,c]]))
def GateZ(a):# GateX for angle 2aπ
    alpha = a*np.pi # half-angle
    c = np.cos(alpha)
    s = 1j*np.sin(alpha)
    return MyArrayClass(np.array([[c-s,0],[0,c+s]]))

def update_arrow(v,a=None,**kwargs):
    x,y,z = 0,0,0
    if v is not None:
        x,y,z = v.coord()
    if a is None:
        return Arrow3D([0,x],[0,y],[0,z],**kwargs)
    a.update(x,y,z)
    return a

def Sphere(n_meridians=20,n_latitudes=None):
    if n_latitudes is None:
        n_latitudes = max(n_meridians/2,4)
    u,v = np.mgrid[0:2*np.pi:n_meridians*1j,0:np.pi:n_latitudes*1j]
    sv = np.sin(v)
    x = np.cos(u) * sv
    y = np.sin(u) * sv
    z = np.cos(v)
    return x,y,z

if __name__=='__main__':
    fig = plt.figure()

    H,W = 2,3
    h0,w0 = 1,1
    h3,w3 = 2,2

    ax0 = plt.subplot2grid((H,W),(0,0),rowspan=h0,colspan=w0,fig=fig)
    ax0.set_aspect('equal')
    ax0.set_xlim(-1.3,1.3)
    ax0.set_ylim(-1.3,1.3)
    ax0.set_axis_off()
    ax0.add_artist(Circle((0,0),1.))
    handle0 = Arrow(0,1)
    ax0.add_artist(handle0)

    ax1 = plt.subplot2grid((H,W),(1,0),rowspan=h0,colspan=w0,fig=fig)
    ax1.set_aspect('equal')
    ax1.set_xlim(-1.3,1.3)
    ax1.set_ylim(-1.3,1.3)
    ax1.set_axis_off()
    ax1.add_artist(Circle((0,0),1.))
    handle1 = Arrow(0,0)
    ax1.add_artist(handle1)

    ax3 = plt.subplot2grid((H,W),(0,1),rowspan=h3,colspan=w3,fig=fig,projection='3d')
    ax3.set_aspect('equal')
    ax3.set_axis_off()
    a0 = [0,0]
    ac = [-1,1.1]
    ax3.add_artist(Arrow3D(ac,a0,a0))
    ax3.add_artist(Arrow3D(a0,ac,a0))
    ax3.add_artist(Arrow3D(a0,a0,ac))
    ax3.plot_wireframe(*Sphere(),color='r',alpha=.3)

    states = [Ket0,None]
    arrows = [None,None]
    trace = [None]
    arrows[0] = update_arrow(states[0],color='b')
    arrows[1] = update_arrow(states[1],color='g')
    ax3.add_artist(arrows[0])
    ax3.add_artist(arrows[1])

    gate = [GateZ,0.]

    def update_trace(x,y,z):
        t = trace[0]
        if t is None:
            trace[0] = ax3.plot(x,y,z,color='g')[0]
        else:
            t.set_xdata(x)
            t.set_ydata(y)
            t.set_3d_properties(z)
    def update_final_state(time=2.,steps=0):
        vsteps = steps if steps else 30
        angles = np.linspace(0.,gate[1],num=vsteps)
        _states = []
        _x,_y,_z  = [],[],[]
        for angle in angles:
            _states.append(gate[0](angle)*states[0])
            x,y,z = _states[-1].coord()
            _x.append(x)
            _y.append(y)
            _z.append(z)
        if steps:
            interval = time/steps
            angles = np.linspace(0.,gate[1],num=steps)
            for i,state in enumerate(_states):
                states[1] = state
                arrows[1] = update_arrow(states[1],arrows[1])
                update_trace(_x[:i+1],_y[:i+1],_z[:i+1])
                plt.pause(interval)
        Gate = gate[0](gate[1])
        states[1] = Gate*states[0]
        arrows[1] = update_arrow(states[1],arrows[1])
        update_trace(_x,_y,_z)
        fig.canvas.draw()
    def on_click_handler(event):
        update_initial_state(axes=event.inaxes,button=event.button,xdata=event.xdata,ydata=event.ydata)
    def update_initial_state(axes=None,button=1,xdata=0.,ydata=0.):
        if axes in [ax0,ax1]:
            steps = 1
            if button == 3:
                steps = 50
            if axes is ax0:
                h0,h1 = handle0,handle1
                k0,k1 = Ket0,Ket1
            else:
                h0,h1 = handle1,handle0
                k0,k1 = Ket1,Ket0
            x0,y0 = h0._verts
            x0,y0 = y0,-x0
            xf,yf = ydata,-xdata
            nf = xf*xf+yf*yf
            if nf > 1.:
                nf = 1/np.sqrt(nf)
                xf,yf = nf*xf,nf*yf
            dx,dy = (xf-x0),(yf-y0)
            dx,dy = np.linspace(0.,dx,num=steps+1)[1:],np.linspace(0.,dy,num=steps+1)[1:]
            for i in range(steps):
                if i:
                    plt.pause(.02)
                x,y = x0+dx[i],y0+dy[i]
                n = x*x+y*y
                z = np.sqrt(max(0.,1.-n))
                h0.update(-y,x)
                h1.update(0,z)
                states[0] = (x+1j*y)*k0 + z*k1
                arrows[0] = update_arrow(states[0],arrows[0])
                update_final_state()
        return True
    fig.canvas.mpl_connect('button_press_event',on_click_handler)

    axA = fig.add_axes([.2,.9,.6,.05])
    slA = Slider(axA,'Angle',-180,180,valinit=360*gate[1])
    def update_angle(value):
        gate[1] = value/360.
        update_final_state()
    slA.on_changed(update_angle)

    axR = fig.add_axes([.01,.88,.1,.1])
    gate_dict = odict([('X',GateX),('Y',GateY),('Z',GateZ)])
    rbR = RadioButtons(axR,tuple(gate_dict),active=2)
    def update_gate(value):
        gate[0] = gate_dict[value]
        update_final_state()
    rbR.on_clicked(update_gate)

    axI = fig.add_axes([.01,.6,.1,.25])
    sq2 = .5*np.sqrt(2.)
    vectors_dict = odict([('0',(ax0,0,1)),('1',(ax1,0,1)),\
            ('+',(ax0,0,sq2)),('-',(ax0,0,-sq2)),\
            ('0+i1',(ax0,sq2,0)),('0-i1',(ax0,-sq2,0))])
            # ('0+i1',(ax1,-sq2,0)),('0-i1',(ax1,sq2,0))])
    rbI = RadioButtons(axI,tuple(vectors_dict),active=0)
    def update_initial(value):
        ax,xd,yd=vectors_dict[value]
        update_initial_state(axes=ax,button=3,xdata=xd,ydata=yd)
    rbI.on_clicked(update_initial)

    axP = fig.add_axes([.01,.3,.1,.25])
    angles_dict = odict([('-Pi',-180),('-Pi/2',-90),\
            ('0',0),('Pi/2',90),('Pi',180)])
    rbP = RadioButtons(axP,tuple(angles_dict),active=2)
    def update_anglebutton(value):
        slA.set_val(angles_dict[value])
    rbP.on_clicked(update_anglebutton)

    plt.show()
