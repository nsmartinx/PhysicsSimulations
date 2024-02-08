from direct.showbase.ShowBase import ShowBase
from panda3d.core import PerspectiveLens, WindowProperties
from direct.showbase.ShowBase import ShowBase

confVars = """
win-size 1280 720
show-frame-rate-meter True
"""

global moveSpeed
global mouseSensitivity
moveSpeed = float(100)
mouseSensitivity = float(50)

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.scene = self.loader.loadModel("models/environment") #loads the environment, not required but makes it easier to orient yourself
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)
        
        Game.movement(self)

        
    def movement(self):
        self.xray_mode = False
        self.show_model_bounds = False
        
        base.disableMouse() #disables default mouse control
       
        props = WindowProperties()
        props.setCursorHidden(True) #hides the cursor
        base.win.requestProperties(props)
        
        # Setup controls
        self.keys = {}
        for key in ['a', 'd', 'w', 's', 'c', 'space']:
            self.keys[key] = 0 #array that stores the state of the above keys (1 is pressed down, 0 is not)
            self.accept(key, self.push_key, [key, 1])
            self.accept('shift-%s' % key, self.push_key, [key, 1]) #if the key is pressed or the key is pressed with shift, it will be registered
            self.accept('%s-up' % key, self.push_key, [key, 0])
        self.accept('escape', __import__('sys').exit, [0]) #closes program if escape is pressed

        # Setup camera
        self.lens = PerspectiveLens()
        self.lens.setFov(60)
        self.lens.setNear(0.01)
        self.lens.setFar(1000.0)
        self.cam.node().setLens(self.lens)
        self.camera.setPos(-9, -0.5, 1)
        self.heading = -95.0
        self.pitch = 0.0

        self.taskMgr.add(self.update, 'main loop')

    def push_key(self, key, value):
        self.keys[key] = value

    def update(self, task):
        mw = base.mouseWatcherNode
        x = 0
        y = 0
        if mw.hasMouse():
        # get the position relative to centre
            x, y = mw.getMouseX(), mw.getMouseY()

        # move mouse back to center
            props = base.win.getProperties()
            base.win.movePointer(0, props.getXSize() // 2, props.getYSize() // 2)
        
        
        delta = globalClock.getDt()
        move_x = delta * moveSpeed * self.keys['d'] - delta * moveSpeed * self.keys['a']
        move_z = delta * moveSpeed * self.keys['w'] - delta * moveSpeed * self.keys['s']
        move_y = delta * moveSpeed * self.keys['space'] - delta * moveSpeed * self.keys['c']
        self.camera.setPos(self.camera, move_x, move_z, move_y)
        self.heading += (-x * mouseSensitivity)
        if (self.pitch + y * mouseSensitivity > 90):
            self.pitch = 90
        elif (self.pitch + y * mouseSensitivity < -90):
            self.pitch = -90
        else:
            self.pitch += (y * mouseSensitivity)
        self.camera.setHpr(self.heading, self.pitch, 0)
        return task.cont  

    
game = Game()
game.run()