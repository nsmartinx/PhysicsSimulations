from direct.showbase.ShowBase import ShowBase
from panda3d.core import ClockObject, LVector3f, LPlanef, LPoint3f, GeomVertexFormat, GeomVertexData, Geom, GeomTriangles, GeomVertexWriter,GeomNode, PerspectiveLens, LVector3, LPoint3d, WindowProperties, loadPrcFileData
from copy import deepcopy

confVars = """
win-size 1280 720
show-frame-rate-meter True
""" #makes the window 720p and turns on the fps counter
loadPrcFileData("", confVars)

global moveSpeed, mouseSensitivity
moveSpeed = float(100) #speed that the camera moves around
mouseSensitivity = float(50) #sensitivity for looking around     

class Box:
    def __init__(self, l, w, h, x, y, z, yaw, pitch, roll): #l, w, h are the length width and height of the box (respectively), x, y, z are the coordinates of the centre of the box, yaw, pitch, roll are the rotation of the box
        self.velocity = LVector3(0, 0, 0)
        self.rotationalVelocity = LVector3(0, 0, 0)

        self.originalPoints = [LPoint3f(-l/2, -w/2, -h/2), LPoint3f(-l/2, w/2, -h/2), LPoint3f(l/2, w/2, -h/2), LPoint3f(l/2, -w/2, -h/2), LPoint3f(-l/2, -w/2, h/2), LPoint3f(-l/2, w/2, h/2), LPoint3f(l/2, w/2, h/2), LPoint3f(l/2, -w/2, h/2)] #stores the original position of all of the points, this is used when calculating the position of the points after a rotation
        
        self.pointIndex = [[5, 4, 0, 1], [7, 6, 2, 3], [6, 5, 1, 2], [4, 7, 3, 0], [6, 7, 4, 5], [1, 0, 3, 2]]#stores which points on the box correspons to each face
        
        snode = GeomNode('box')#creates the geomnode (visual representation of the box)
        for i in range(6):
            snode.addGeom(Collision.makeQuadrilateral(self, self.originalPoints[self.pointIndex[i][0]], self.originalPoints[self.pointIndex[i][1]], self.originalPoints[self.pointIndex[i][2]], self.originalPoints[self.pointIndex[i][3]]))
                
        #render the box to the screen
        boxObject = render.attachNewNode(snode)
        boxObject.setTwoSided(True)
        self.boxModel = boxObject
        
        self.boxModel.setPos(x, y, z)#changes the position of the box to the inputted location
        self.boxModel.setHpr(yaw, pitch, roll)
    
    
class Collision(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        Collision.movement(self) #enables camera control with wasd and mouse
        
        self.scene = self.loader.loadModel("models/environment") #loads the environment, not required but makes it easier to orient yourself
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)
       
        global box0
        box0 = Box(6, 6, 6, -20, 0, 20, 23, 10, 45)
        box0.velocity = LVector3(5, 0, 0)
        box0.rotationalVelocity = LVector3(20, 30, 80)
        
       
    def movement(self):#enables camera and movement controls. Move the mouse to control the camera, wasd are to move forward, backwards, left right, c is to move down, space is to move up. All movements are relative to the cameras current dirction       
        base.disableMouse() #disables default mouse control
       
        props = WindowProperties()
        props.setCursorHidden(True) #hides the cursor
        base.win.requestProperties(props)
 
        # Setup controls. 
        self.keys = {} #this array will store the state of all desired keys (1 is pressed, 0 is not)
        for key in ['a', 'd', 'w', 's', 'c', 'space']:
            self.keys[key] = 0 #defaults key to not be pressed
            self.accept(key, self.push_key, [key, 1])#if the key is pressed
            self.accept('%s-up' % key, self.push_key, [key, 0]) #when the key is released
        self.accept('escape', __import__('sys').exit, [0]) #closes program if escape is pressed

        #Configure Camera
        self.lens = PerspectiveLens()
        self.lens.setFov(60)
        self.lens.setNear(0.01)
        self.lens.setFar(1000.0)
        self.heading = 0.0
        self.pitch = 0.0

        #update will update the camera position every frame
        self.taskMgr.add(self.movementUpdate, 'movement')

    def push_key(self, key, value): #function to change state of keys array
        self.keys[key] = value

    def movementUpdate(self, task):
        mw = base.mouseWatcherNode
        x, y = 0, 0
        if mw.hasMouse():            
            x, y = mw.getMouseX(), mw.getMouseY() #get the position of the mouserelative to centre
            props = base.win.getProperties()
            base.win.movePointer(0, props.getXSize() // 2, props.getYSize() // 2) #move the mouse back to the centre
       
       
        delta = globalClock.getDt() #time since last frame
        move_x = delta * (moveSpeed * self.keys['d'] - moveSpeed * self.keys['a']) #calculates how much to move the camera on each axis
        move_z = delta * (moveSpeed * self.keys['w'] - moveSpeed * self.keys['s'])
        move_y = delta * (moveSpeed * self.keys['space'] - moveSpeed * self.keys['c'])
        self.camera.setPos(self.camera, move_x, move_z, move_y) #moves the camera realtive to the cameras current position and orientation
        self.heading -= (x * mouseSensitivity) #how much to move the camera horizontally
        
        if (self.pitch + y * mouseSensitivity > 90): #clamps the vertical movement so it can't exceed straight up or straight down
            self.pitch = 90
        elif (self.pitch + y * mouseSensitivity < -90):
            self.pitch = -90
        else:
            self.pitch += (y * mouseSensitivity) #how much to move the camera vertically
            
        self.camera.setHpr(self.heading, self.pitch, 0)
        
        return task.cont  
 
    def makeQuadrilateral(self, point1, point2, point3, point4): #input the four points (LPoint3d) that a quadrilateral will be drawn between. Ensure that the four points make a U shape if you were to draw a line between them (Not an N or X shape)
            format = GeomVertexFormat.getV3cp() #this format contains vertex location and colour of the vertex
            vdata = GeomVertexData('square', format, Geom.UHDynamic)

            vertex = GeomVertexWriter(vdata, 'vertex')#writers for the vertex and the colour
            colour = GeomVertexWriter(vdata, 'color')

            for point in [point1, point2, point3, point4]:
                vertex.addData3(point[0], point[1], point[2]) #adds the position of the four vertexes

            # adding different colors to the vertex for visibility. These colours are expressed in RGBA.
            colour.addData4f(0, 0, 1, 1)
            colour.addData4f(0, 0, 1, 1)
            colour.addData4f(0, 0.5, 1, 1)
            colour.addData4f(0.5, 0, 1, 1)

            tris = GeomTriangles(Geom.UHDynamic) #creates two triangles to represent the quadrilateral
            tris.addVertices(0, 1, 3)
            if(point1 != point3): #if points 1 and 3 are the same, it will only generate one triangle
                tris.addVertices(1, 2, 3)

            square = Geom(vdata)
            square.addPrimitive(tris)#combines the triangles into one quadrilateral
            
            return square

Collision().run()