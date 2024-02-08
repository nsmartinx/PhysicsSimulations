from direct.showbase.ShowBase import ShowBase
from panda3d.core import ClockObject, GeomVertexFormat, GeomVertexData, Geom, GeomTriangles, GeomVertexWriter,GeomNode, PerspectiveLens, LVector3, LPoint3d, WindowProperties, loadPrcFileData
from math import cos, sin, pi, sqrt

confVars = """
win-size 1820 1024
show-frame-rate-meter True
""" #makes the window 720p and turns on the fps counter
loadPrcFileData("", confVars)

global fps, moveSpeed, mouseSensitivity
fps = 120 #fps is the framerate for the physics simulation, the visuals will attempt to render at 60 fps
moveSpeed = float(100) #speed that the camera moves around
mouseSensitivity = float(50) #sensitivity for looking around

class Sphere:
    def __init__(self, x, y, z, r, p, m): #x, y, z are the coordinates of the centre of the sphere, r is the radius, p is the precision (number of points in a semicircle). Minimum value of p is 2. m is the mass
        self.velocity = LVector3(0, 0, 0)
        self.radius = r
        self.mass = m
        self.position = LVector3(x, y, z)
       
        sphere = list()#this will be a list of lists of points. Each of the lists of points will be one semicircle of the sphere.
        for i in range(2 * p):#each semi circle
            semicircle = [LPoint3d(0, 0, 0)] * (p - 1) #creates a list of points and sets them all to equal zero
            for j in range(p - 1): #each point within the semi circle
                ang1 = pi * (i / p)#two component angles of position on sphere
                ang2 = (pi / 2) - pi * ((j + 1) / p)
                semicircle[j] = LPoint3d((r * cos(ang2) * cos(ang1)), (r * cos(ang2) * sin(ang1)), (r * sin(ang2)))#calculates the x, y, and z values of the point represented by the two angles
            sphere.append(semicircle)#adds the semicircle of points to the sphere
            
        snode = GeomNode('sphere')#creates an empty geomnode that will contain the sphere
        for i in range(2 * p):#creates quadrilaterals for every point on the sphere
            for j in range(p - 2):
                o = i + 1
                if (o >= 2 * p):
                    o = 0
                snode.addGeom(Collision.makeQuadrilateral(self, sphere[i][j], sphere[i][j + 1], sphere[o][j + 1], sphere[o][j]))
                
        #the top and bottom points of the sphere have not been added yet
        top = LPoint3d(0, 0, r) #top point
        bottom = LPoint3d(0, 0, -r) # bottom point
        for i in range(2 * p): #adds triangles betweent the top/bottom point and all neighbooring points
            o = i + 1
            if (o >= 2 * p):
                o = 0
            snode.addGeom(Collision.makeQuadrilateral(self, top, sphere[i][0], top, sphere[o][0])) #because the first and third are both top, only a triangle will be generated
            snode.addGeom(Collision.makeQuadrilateral(self, bottom, sphere[i][p - 2], bottom, sphere[o][p - 2]))
            
        #render the sphere to the screen
        sphereObject = render.attachNewNode(snode)
        sphereObject.setTwoSided(True)
        self.sphereModel = sphereObject
        
        self.sphereModel.setPos(x, y, z)#changes the position of the sphere to the inputted location, Important not to generate the sphere at the desired location as the reference point will always start at (0, 0, 0). Generating the sphere at the origin then moving it after fixes this.
    def configure(self, x, y, z, m, vx, vy, vz):
        self.position = LVector3(x, y, z)
        self.mass = m
        self.velocity = LVector3(vx, vy, vz)
        
    def updatePosition(self, frameTime): #call this from the physics update function, will automatically move the sphere the amount specified by the velocity. If you want to add acceleration, use this same code except with acceleration/velocity instead of velocity/position
        global fps
        self.position += self.velocity * frameTime
        self.sphereModel.setPos(self.position)
        

           
class Collision(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        Collision.movement(self) #enables camera control with wasd and mouse
        
        self.scene = self.loader.loadModel("models/environment") #loads the environment, not required but makes it easier to orient yourself
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)
        
        global spheres, clock, previousTime, clock1, previousTime1, time, simNumber, setSim
        spheres = list()
        
        spheres.append(Sphere(20, 0, 20, 2, 8, 1))
        spheres.append(Sphere(-20, 0, 20, 2, 8, 1))
        spheres.append(Sphere(0, 0, 200, 1, 8, 1))
        spheres.append(Sphere(0, 0, 200, 5, 8, 1))
        
        spheres[0].velocity = (LVector3(-5, 0, 0))
        spheres[1].velocity = (LVector3(5, 0, 0))
        spheres[2].velocity = (LVector3(0, 0, 0))
        spheres[3].velocity = (LVector3(0, 0, 0))
        
        clock = ClockObject()
        clock1 = ClockObject()
        previousTime = 0
        previousTime1 = 0
        time = 0
        
        simNumber = 0
        setSim = -1
        
        global fps
        self.taskMgr.doMethodLater(1/fps, self.physicsUpdate, 'physics') #every 1/fps seconds calls physicsUpdate
        
        
    def physicsUpdate(self, task): #this will be called fps times per second
        global clock, previousTime, simNumber, spheres, setSim
        frameTime = clock.get_real_time() - previousTime
        previousTime = clock.get_real_time()#time since previous fram (Delta time)
        
        simTime = 8
        simCount = 10
        
        if(previousTime % (simTime * simCount) < simTime * 1):
            simNumber = 0
        elif(previousTime % (simTime * simCount) < simTime * 2):
            simNumber = 1
        elif(previousTime % (simTime * simCount) < simTime * 3):
            simNumber = 2
        elif(previousTime % (simTime * simCount) < simTime * 4):
            simNumber = 3
        elif(previousTime % (simTime * simCount) < simTime * 5):
            simNumber = 4
        elif(previousTime % (simTime * simCount) < simTime * 6):
            simNumber = 5
        elif(previousTime % (simTime * simCount) < simTime * 7):
            simNumber = 6
        elif(previousTime % (simTime * simCount) < simTime * 8):
            simNumber = 7
        elif(previousTime % (simTime * simCount) < simTime * 9):
            simNumber = 8
        elif(previousTime % (simTime * simCount) < simTime * 10):
            simNumber = 9
            
        if (simNumber == 0 and setSim != 0):
            setSim = 0
            spheres[0].configure(20, 0, 20, 1, -5, 0, 0)
            spheres[1].configure(-20, 0, 20, 1, 5, 0, 0)
            spheres[2].configure(0, 0, 200, 1, 0, 0, 0)
            spheres[3].configure(0, 0, 200, 1, 0, 0, 0)
        if (simNumber == 1 and setSim != 1):
            setSim = 1
            spheres[0].configure(20, 0, 20, 1, -5, 0, 0)
            spheres[1].configure(-20, 0, 20, 1, 5, 0, 0)
            spheres[2].configure(0, 0, 30, 1, 0, 0, -1)
            spheres[3].configure(0, 0, 15, 4, 0, 0, 0)
        if (simNumber == 2 and setSim != 2):
            setSim = 2
            spheres[0].configure(20, 3, 20, 1, -5, 0, 0)
            spheres[1].configure(-18, 0, 20, 1, 5, 0, 0)
            spheres[2].configure(0, 0, 20, 9, 0, 0, 0)
            spheres[3].configure(0, 0, 200, 1, 0, 0, 0)
        if (simNumber == 3 and setSim != 3):
            setSim = 3
            spheres[0].configure(0, 0, 20, 1, 0, 0, 0)
            spheres[1].configure(-20, 0, 20, 1, 0, 0, 0)
            spheres[2].configure(0, 0, 200, 1, 0, 0, 0)
            spheres[3].configure(20, 0, 20, 100, -5, 0, 0)
        if (simNumber == 4 and setSim != 4):
            setSim = 4
            spheres[0].configure(-14, 14, 21, 1, 3.5, -3.5, 0)
            spheres[1].configure(14, 14, 19, 1, -3.5, -3.5, 0)
            spheres[2].configure(0, -20, 20, 1, 0, 7, 0)
            spheres[3].configure(0, 0, 200, 1, 0, 0, 0)
        if (simNumber == 5 and setSim != 5):
            setSim = 5
            spheres[0].configure(-14, 14, 21, 1, 3.5, -3.5, 0)
            spheres[1].configure(14, 14, 19, 1, -3.5, -3.5, 0)
            spheres[2].configure(0, -20, 20, 1, 0, 7, 0)
            spheres[3].configure(0, 0, 20, 1, 0, 0, 0)
        if (simNumber == 6 and setSim != 6):
            setSim = 6
            spheres[0].configure(-3, 3, 21, 1, 0, 0, 0)
            spheres[1].configure(3, 3, 19, 1, 0, 0, 0)
            spheres[2].configure(0, -5, 20, 1, 0, 0, 0)
            spheres[3].configure(0, 0, 40, 4, 0, 0, -5)
        if (simNumber == 7 and setSim != 7):
            setSim = 7
            spheres[0].configure(0, -20, 21, 5, 0, 5, 0)
            spheres[1].configure(0, 0, 200, 1, 0, 0, 0)
            spheres[2].configure(0, 18, 19, 1, 0, -7, 0)
            spheres[3].configure(0, 0, 200, 4, 0, 0, 0)
        if (simNumber == 8 and setSim != 8):
            setSim = 8
            spheres[0].configure(0, 0, 20, 4, 0, 0, 0)
            spheres[1].configure(0, 0, 200, 1, 0, 0, 0)
            spheres[2].configure(0, 18, 19, 1, 0, -7, 0)
            spheres[3].configure(0, -20, 21, 8, 0, 5, 0)
        if (simNumber == 9 and setSim != 9):
            setSim = 9
            spheres[0].configure(20, 0, 22, 4, -5, 0, 0)
            spheres[1].configure(-20, 0, 18, 1, 5, 0, 0)
            spheres[2].configure(0, -20, 20, 1, 0, 3, 0)
            spheres[3].configure(0, 20, 20, 8, 0, -5, 0)
        
        
        for s0 in range(spheres.__len__()):
            for s1 in range(s0 + 1, spheres.__len__()):
                distance = (spheres[s0].position - spheres[s1].position).length()
                distance1 = (spheres[s0].position + (spheres[s0].velocity / fps) - spheres[s1].position - (spheres[s1].velocity / fps)).length()  
                collisionCheck = (distance1 < distance)

                if (distance < spheres[s0].radius + spheres[s1].radius and collisionCheck):
                    vel0 = spheres[s0].velocity
                    vel1 = spheres[s1].velocity
                    between = spheres[s1].position - spheres[s0].position
                    mass0 = spheres[s0].mass
                    mass1 = spheres[s1].mass
    
                    x0 = vel0.project(between)
                    x1 = vel1.project(between)
    
                    mul0 = ((mass0 - mass1) / (mass0 + mass1))
                    mul1 = ((2 * mass1) / (mass0 + mass1))
                    mul2 = ((mass1 - mass0) / (mass0 + mass1))
    
                    fx0 = LVector3(x0[0] * mul0, x0[1] * mul0, x0[2] * mul0) + LVector3(x1[0] * mul1, x1[1] * mul1, x1[2] * mul1)
                    fx1 = LVector3(x0[0] * mul1, x0[1] * mul1, x0[2] * mul1) + LVector3(x1[0] * mul2, x1[1] * mul2, x1[2] * mul2)
    
                    spheres[s0].velocity = (vel0 - x0 + fx0)
                    spheres[s1].velocity = (vel1 - x1 + fx1)
                    
        for sphere in spheres:
            sphere.updatePosition(frameTime)
            
        return task.again #tells the function to run again after the specified delay (1/fps seconds)
    
    def movement(self):#enables camera and movement controls. Move the mouse to control the camera, wasd are to move forward, backwards, left right, c is to move down, space is to move up. All movements are relative to the cameras current dirction       
        
        base.disableMouse() #disables default mouse control
       
        props = WindowProperties()
        props.setCursorHidden(True) #hides the cursor
        base.win.requestProperties(props)
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
        global clock1, previousTime1
        frameTime1 = clock1.get_real_time() - previousTime1
        previousTime1 = clock1.get_real_time()#time since previous fram (Delta time)
        
        speed = 0.1
        distance = 50
        global time
        time += frameTime1
        self.camera.setPos(LVector3(distance * cos(time * speed), distance * sin(time * speed), 45))
        self.camera.setHpr(90+time * 180 / pi * speed, -28, 0)
        
        
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