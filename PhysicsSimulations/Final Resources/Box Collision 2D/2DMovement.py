from direct.showbase.ShowBase import ShowBase
from panda3d.core import LPoint2f, LVector2, ClockObject, LVector3f, LPlanef, LPoint3f, GeomVertexFormat, GeomVertexData, Geom, GeomTriangles, GeomVertexWriter,GeomNode, OrthographicLens, LVector3, LPoint3d, WindowProperties, loadPrcFileData
from copy import deepcopy


confVars = """
win-size 1280 720
show-frame-rate-meter True
""" #makes the window 720p and turns on the fps counter
loadPrcFileData("", confVars)

global moveSpeed
moveSpeed = float(100) #speed that the camera moves around
    
    
class Collision(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        Collision.movement(self) #enables camera control with wasd and mouse
        
        self.scene = self.loader.loadModel("models/environment") #loads the environment, not required but makes it easier to orient yourself
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 500, 0)
               
    def movement(self):#enables camera and movement controls. Move the mouse to control the camera, wasd are to move forward, backwards, left right, c is to move down, space is to move up. All movements are relative to the cameras current dirction       
        base.disableMouse() #disables default mouse control
       
        props = WindowProperties()
        props.setCursorHidden(True) #hides the cursor
        base.win.requestProperties(props)
 
        # Setup controls. 
        self.keys = {} #this array will store the state of all desired keys (1 is pressed, 0 is not)
        for key in ['a', 'd', 'w', 's']:
            self.keys[key] = 0 #defaults key to not be pressed
            self.accept(key, self.push_key, [key, 1])#if the key is pressed
            self.accept('%s-up' % key, self.push_key, [key, 0]) #when the key is released
        self.accept('escape', __import__('sys').exit, [0]) #closes program if escape is pressed

        #Configure Camera
        self.lens = OrthographicLens()
        lensSize = 5
        self.lens.setFilmSize(16 * lensSize, 9 * lensSize)
        self.lens.setNear(-1000.0)
        self.lens.setFar(1000.0)
        self.cam.node().setLens(self.lens)

        #update will update the camera position every frame
        self.taskMgr.add(self.movementUpdate, 'movement')

    def push_key(self, key, value): #function to change state of keys array
        self.keys[key] = value

    def movementUpdate(self, task):
        delta = globalClock.getDt() #time since last frame
        move_x = delta * (moveSpeed * self.keys['d'] - moveSpeed * self.keys['a']) #calculates how much to move the camera on each axis
        move_z = delta * (moveSpeed * self.keys['w'] - moveSpeed * self.keys['s'])
        
        self.camera.setPos(self.camera, move_x, 0, move_z) #moves the camera realtive to the cameras current position and orientation
        
        return task.cont  

Collision().run()