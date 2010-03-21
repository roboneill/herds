import maya.cmds as cmds
import maya.mel as mel
import random

class herds():
	'''
	HERDS: Relational Motion Tool
	Version 3.0
	Rob O'Neill (rob@morphometric.com)
	http://www.morphometric.com/research/herds/
	
	Started:	
	Updated: 	01/01/2010 
	Description:	A small application for Maya to simulate the
			herding behaviors of some large terrestrial animals.
			At this stage it still looks like flocking.
	
	Anyone can use and modify this script at their own risk.  If you use it
	for a project please drop me a note as I'd love to see it in action.  In
	the same respect, if you turn this into something else, let me know.
	
	Thanks:	Kevin Mannens for the Version 2.5 update!
	
	
	Todo/Bugs:
	Cycle check
	Tab removal
	Offset particle from herdmaster for dynamics
	Dynamics on agents
	Geometry support - direction, sub animation
	Fold in mannens edits
	Fold in dlam edits

	Bugs
	ButtonManip is not named
	Make rebuild work after a scene close/reopen

	'''
	
	def __init__(self, name='herds_ui'):
		self.herdsTitle = 'H E R D S'
		self.herdsVersion = '3.0'
		self.width = 350
		self.height = 350
		self.name = name
	
	def ui(self):
	
		if(self.query()):
			self.deleteui()
		
		# Constants for "Number of Herd Members"
		# Defines the number of members in the simulated herd.
		MIN_MEMB = 0
		MAX_MEMB = 200
		DEF_MEMB = 10
	
		# Constants for "Stray"
		# Defines the variables for amount that nodes stray from the herd.
		MIN_STRAY = 0.0
		MAX_STRAY = 100.0
		DEF_STRAY = 10.0
	
		# Constants for "Frame Offset"
		# Defines the amount of frame offset that objects in relation to the leader.
		MIN_OFF = 0.0
		MAX_OFF = 10.0 #each node starts 10 frames after the one before it
		DEF_OFF = 1.0
	
		# Constants for "Leader Focus"
		# Defines the amount in which the herd attempts to maintain the leaders xyz position
		MIN_FOCUS = 0.0
		MAX_FOCUS = 1.0
		DEF_FOCUS = 0.5
	
		# Constants for "Randomness"
		# Defines the degree of time based randomness in the herd.
		MIN_RANDOMNESS = 0.0
		MAX_RANDOMNESS = 1.0
		DEF_RANDOMNESS = 0.5
	
			
		cmds.window(self.name, maximizeButton=False, resizeToFitChildren=True, sizeable=True, height=
			self.height, width=self.width, title=(self.herdsTitle + " " + self.herdsVersion), 
			iconName="Herds")

		cmds.formLayout("mainForm")
		cmds.tabLayout("tab")
	
		cmds.formLayout("mainForm", e=True, af=[('tab', 'top', 5), ('tab', 'left', 5), ('tab', 'right', 5), ('tab', 'bottom', 5)])

		cmds.frameLayout("MainTab", labelVisible=0, collapsable=0, borderStyle="etchedIn")

		cmds.columnLayout('mainColumnLayout', adjustableColumn=0, columnAttach=("left", 0), rowSpacing=0, columnWidth=self.width, columnAlign="left")
		

		cmds.setParent("mainColumnLayout")

		cmds.frameLayout("variableFrameLayout", label="Herd Variables", labelVisible=True, labelAlign="center", labelIndent=0, borderVisible=False,
			borderStyle="etchedOut", collapsable=False, collapse=False)

		cmds.columnLayout("variableColumnLayout", adjustableColumn=1, columnAttach=("both", 0), rowSpacing=0, columnWidth=self.width, columnAlign="left")
		
		cmds.rowLayout(numberOfColumns=4, columnAttach4=("both", "both", "both", "both"))
		cmds.setParent( ".." )

		cmds.intSliderGrp('membcapacity', label="Members #", field=True, value=DEF_MEMB, minValue=MIN_MEMB, maxValue=MAX_MEMB, sliderStep=DEF_MEMB, fieldStep=DEF_MEMB,
		fieldMinValue=MIN_MEMB, fieldMaxValue=MAX_MEMB, ct3=("left", "both", "left"), cw3=(100, 40, 200), columnOffset3=(8, 0, 0))

		cmds.floatSliderGrp("sliderStray", label="Stray", field=True, precision=1, value=DEF_STRAY, minValue=MIN_STRAY, maxValue=MAX_STRAY, sliderStep=1,
		ct3=("left", "both", "left"), cw3=(100, 40, 200), columnOffset3=(8, 0, 0), dragCommand=self.herdsEditMotion)
		
		cmds.floatSliderGrp("sliderFocus", label="Leader Focus", field=True, precision=1, value=DEF_FOCUS, minValue=MIN_FOCUS, maxValue=MAX_FOCUS, sliderStep=0.1, fieldStep=0.1, 
		fieldMinValue=MIN_FOCUS, fieldMaxValue=MAX_FOCUS, ct3=("left", "both", "left"), cw3=(100, 40, 200), columnOffset3 =(8, 0, 0), dragCommand=self.herdsEditMotion)

		cmds.floatSliderGrp("sliderOffset", label="Frame Offset", field=True, precision=1, value=DEF_OFF, minValue=MIN_OFF, maxValue=MAX_OFF,
		sliderStep=0.1, ct3=("left", "both", "left"), cw3=(100, 40, 200), columnOffset3=(8, 0, 0), dragCommand=self.herdsEditMotion)
		
		cmds.floatSliderGrp("sliderRandomness", label="Randomness", field=True, precision=1, value=DEF_RANDOMNESS, minValue=MIN_RANDOMNESS,
		maxValue=MAX_RANDOMNESS, sliderStep=0.1, fieldStep=0.1, fieldMinValue=MIN_RANDOMNESS, fieldMaxValue=MAX_RANDOMNESS,
		ct3=("left", "both", "left"), cw3=(100, 50, 200), columnOffset3=(8, 0, 0), dragCommand=self.herdsEditMotion)

		cmds.columnLayout("variableColumnLayout", adjustableColumn=1, columnAttach=("both", 0), rowSpacing=0, columnWidth=self.width,
		columnAlign="center")
		
		cmds.button("herdsButton", label="RUN  H E R D S!", width=self.width, align="center", command=self.createHerdCallback)

		cmds.separator()

		cmds.setParent("mainColumnLayout")

		#-----------------------------------------------------
		# Post Creation tab
		#-----------------------------------------------------
		cmds.frameLayout("postCreationFrameLayout", label="Post Creation", labelVisible=True, 
		labelAlign="center", labelIndent=0, borderVisible=False, borderStyle="etchedOut", 
		collapsable=False, collapse=False)
			
		cmds.columnLayout("postCreationColumnLayout", adjustableColumn=1, columnAttach=("both", 0),
		rowSpacing=0, columnWidth=self.width, columnAlign="center")

		cmds.button(label="Find Leader", align="center", width=self.width, command=self.herdsSelectLeader)
		cmds.button(label="Rebuild Herd", align="center", width=self.width, command=self.herdsRebuild)
		
		cmds.rowLayout(width=self.width, numberOfColumns=2, cw2=[self.width * 0.5, self.width * 0.5])
		cmds.button(label="Make Leader Dynamic", align="center", width=(self.width * 0.5), command=self.herdsFollowParticle)
		cmds.button(label="Remove Leader Dynamics", align="center", width=(self.width * 0.5), command=self.herdsRemoveParticle)
		cmds.setParent("postCreationColumnLayout")

		cmds.separator()

		cmds.text(label=("Herds: Relational Motion Tool (v" + self.herdsVersion + ")"))
		cmds.text(label="Rob O'Neill rob@morphometric.com")
		cmds.text(label="http://www.morphometric.com/research/herds/")

		'''
		cmds.setParent("tab")
		cmds.setParent("..")

		cmds.frameLayout("secondTab", labelVisible=0, collapsable=0, borderStyle="etchedIn")
		form=cmds.formLayout()

		cmds.button()
		
		cmds.setParent("secondTab")
		cmds.setParent("..")
	
		cmds.tabLayout("tab", e=True, changeCommand=self.clean, tabLabel=("mainForm", "Herds"), tli=(form, "Help")
		'''
		
		# finish
		self.clean()
		
		cmds.showWindow(self.name)

	
	def query(self):
		if(cmds.window( self.name, exists=True)):
			return 1
		else:
			return 0
		
	def clean(self):
		cmds.window(self.name, e=True, height=self.height, width=self.width)
		
	def deleteui(self):
		cmds.deleteUI(self.name)
	
	def values(self):
		population = cmds.intSliderGrp('membcapacity', q=True, v=True)
		stray = cmds.floatSliderGrp('sliderStray', q=True, v=True)		
		focus = cmds.floatSliderGrp('sliderFocus', q=True, v=True)		
		offset = cmds.floatSliderGrp('sliderOffset', q=True, v=True)
		randomness = cmds.floatSliderGrp('sliderRandomness', q=True, v=True)
		
		# build dictionary
		values = {  "population":population,
					"stray": stray,
					"focus": focus,
					"offset":offset,
					"randomness":randomness
					}
		# return values
		return values

	def herdsSelectLeader(self, *args):
		leaderNode = leader()
		leaderNode.select()

	def herdsEditMotion(self, *args):
		leaderNode = leader()
		leaderNode.editmotion()

	def herdsRebuild(self, *args, **kwargs ):
		
		herddataexists = getattr(self, "herddata", None)
		if herddataexists:
			self.herddata.rebuild()
		else:
			self.herddata = herd()
			self.herddata.rebuild()
		
	def herdsFollowParticle(self, *args):
		leaderNode = leader()
		leaderNode.followParticle()
		
	def herdsRemoveParticle(self, *args):
		leaderNode = leader()
		leaderNode.deleteParticle()

	def createHerdCallback(self, *args, **kwargs ):
		userObj = cmds.ls(sl=True)
		if userObj:
			confirmDialog = cmds.confirmDialog(title="Just Checking...",
				message="Is the nose of your selection pointing in +X?\nDid you freeze all transformations on it?",
		 		button=["Yes","No"],
				defaultButton="Yes",
				cancelButton="No", 
				dismissString="No")

			if confirmDialog == "Yes":		
				self.herddata = herd()
				self.herddata.create(userObj)
		else:
			self.herddata = herd()
			self.herddata.create()


class herd():
	def __init__(self):
		self.debug = 0
		self.herdMaster = leader()
		self.herdMasterNode = self.herdMaster.create()
	
	def create(self, userobj="cone", population=10):
		self.userobj = userobj
		
		# save userobj on leader
		self.herdMaster.recordShape(self.userobj)
		
		# build the agents
		self.agents = self.build()
		
		# return the elements created
		ecosystem = { "leader": self.herdMasterNode,
			     "agents": self.agents }
		
		return ecosystem
			
	def delete(self):
		population = self.getPopulation()
		
		for agent in population:
			if self.debug: print("Herds Deleting " + agent)
			cmds.delete(agent)
	
	def getPopulation(self):
		if(cmds.objExists(self.herdMasterNode)):
			population = cmds.listConnections(self.herdMasterNode + ".leaderMessage")
			return population

	def build(self):
		# if ui
		values = herds().values()
		
		agents = []
		# get population and loop
		for i in range(values["population"]):
			agentMember = agent(self.herdMasterNode)
			agentName = agentMember.create(i, self.userobj)
			agents.append(agentName)
			
			# create message connection between leader and members
			agentMember.register(i)

		return agents

	def rebuild(self):
		self.delete()
		
		self.userobj = cmds.getAttr((self.herdMasterNode + '.shpe'))
		self.build()


class agent(herd): 
	def __init__(self, leader):
		self.leader = leader
		self.nodename = 'herdmemb'
		self.nodeParticleName = (self.nodename + '_particle')
		self.nodeParticleExpressionName = (self.nodeParticleName + '_exp')
		
	def create(self, objnum, shape="cone"):
		if shape == "cone":
			node = cmds.cone(ch=False, n='herdmemb')
		else:
			node = cmds.duplicate(shape, ic=True, n='herdmemb')

		cmds.addAttr(node, sn='fad', ln='frameAdjust', dv=0, k=True)
	
		values = herds().values()
		
		cmds.expression(s=("$herdvar = " + str(random.random() - 0.5) + " * " + self.leader + ".rnds + " + str(objnum) + ";\n"
						+ "$randfac = " + self.leader + ".stry;\n"
						+ "$foc = " + self.leader + ".lf;\n"
						+ "if( $foc != 0 ) {\n"
						+ "$randfac *= min( 1.0,abs($herdvar)*(1-$foc)/($foc*"+ str(values["population"]) +") );}\n"
						+ "$herdvar = $herdvar * -" + self.leader + ".frameOffset + frame +" + node[0] + ".frameAdjust;\n"
						+ "$offset = " + str(random.random() - 0.45) + " * $randfac;\n"
						+ node[0] + ".tx = $offset + `getAttr -time $herdvar " + self.leader + ".tx`;\n" 
						+ "$offset = " + str(random.random() - 0.45) + " * $randfac;\n"
						+ node[0] + ".ty = $offset + `getAttr -time $herdvar " + self.leader + ".ty`;\n" 
						+ "$offset = " + str(random.random() - 0.45) + " * $randfac;\n"
						+ node[0] + ".tz = $offset + `getAttr -time $herdvar " + self.leader + ".tz`;\n"
						), n=(node[0] + "_herd_exp"))
		# Turns off the checker for finding cycles - throws up lots of warnings without it.
		cmds.cycleCheck(e=True, all=False)
		
		self.node = node[0]
		self.point()
		
		return node
		
	def register(self, objnum):
		# connect agent with leader
		cmds.addAttr(self.node, ln="leaderConnection", at="message")
		cmds.connectAttr((self.node + ".message"), (self.leader+ ".leaderMessage[" + str(objnum) + "]"))

	def dynamic(self):
		translateX = cmds.getAttr(self.node + ".tx") 
		translateY = cmds.getAttr(self.node + ".ty")
		translateZ = cmds.getAttr(self.node + ".tz") 

		self.agentparticle = cmds.particle(p=(translateX, translateY, translateZ), n=self.nodeParticleName)
		cmds.xform(cp=True)

		self.agentParticleExpression = cmds.expression(s=("vector $position= `getAttr " + self.nodeParticleName + ".position`;\n" +
			self.node + ".translateX = $position.x;\n" +
			self.node + ".translateY = $position.y;\n" +
			self.node + ".translateZ = $position.z;"), o=self.node, ae=1, uc="all", n=self.nodeParticleExpressionName)

		
	def point(self):

		trans = cmds.getAttr(self.node + ".translate")
		pivot = cmds.getAttr(self.node + ".transMinusRotatePivot")
		pos = [trans[0][0] - pivot[0][0], (trans[0][1] - pivot[0][1]), (trans[0][2] - pivot[0][2])]
		
		# Create a hidden space locator.
		locator = cmds.spaceLocator(name=(self.node + "_direction"))
		cmds.hide(locator[0])
		cmds.parent(locator, self.node)
		cmds.setAttr(locator[0] + ".inheritsTransform", False)
	    
		aim = [-1.0, -0.0, -0.0]		# Notice I have predefined the aim for x
		localUp = [0.0, 1.0, 0.0]	# Notice I have predefined the localup direction for y
		worldUp = [0.0, 1.0, 0.0]	# Notice I have predefined the worldup direction for y

		# Create an aim constraint on the object that always aims away from the locator.
		# aimConstraint constrains an object's orientation to point at a target object 
		
		cmds.aimConstraint(locator[0], self.node, w=1, aimVector=[aim[0], aim[1], aim[2]], 
			upVector=[localUp[0], localUp[1], localUp[2]], 
			worldUpVector=[worldUp[0], worldUp[1], worldUp[2]],
			name="directionConstraint")
		
		# Add attributes to the object for its last x, y, and z positions and an
		# attribute to turn on and off the face forward command for each node. 
		cmds.addAttr(self.node, ln="faceForward", at="bool", k=True, dv=True)
		cmds.addAttr(self.node, ln="lastX", at="double", dv=pos[0])
		cmds.addAttr(self.node, ln="lastY", at="double", dv=pos[0])
		cmds.addAttr(self.node, ln="lastZ", at="double", dv=pos[0])
		
		# The expression that controls all the turning
		cmds.expression(s=(
			"// For some reason the world space position of the object is\n" +
			"// the translation minus the transMinusRotatePivot attributes.\n" +
			"//\n" +
			"float $positionX = translateX - transMinusRotatePivotX;\n" +
			"float $positionY = translateY - transMinusRotatePivotY;\n" +
			"float $positionZ = translateZ - transMinusRotatePivotZ;\n" +
			"\n" +
			"// If the faceForward attribute is off then short circuit the\n" +
			"// aim constraint by putting the locator right on top of the\n" +
			"// object.\n" +
			"//\n" +
			"if (! faceForward)\n" +
			"{\n" +
			"    lastX = $positionX;\n" +
			"    lastY = $positionY;\n" +
			"    lastZ = $positionZ;\n" +
			"}\n" +
			"\n" +
			"// Update the locator to the last world space position of the\n" +
			"// object.\n" +
			"//\n" +
			locator[0] + ".tx = lastX;\n" +
			locator[0] + ".ty = lastY;\n" +
			locator[0] + ".tz = lastZ;\n" +
			"// Update the last position attributes with the current\n" +
			"// position.\n" +
			"//\n" +
			"lastX = $positionX;\n" +
			"lastY = $positionY;\n" +
			"lastZ = $positionZ;\n"
			), o=self.node, name=(self.node + "_faceForward_exp"), ae=0, uc=all)   

	
	def pointall(self):
		cmds.waitCursor(state='on')

		# get population from leader message
		population = herd.getPopulation()		

		for agent in population:
			self.point(agent)

		cmds.waitCursor(state='off')
	

class leader():
	def __init__(self, name="herdmaster"):
		self.leadername = name
		self.leaderParticleName = (name + "_particle")
		self.leaderParticleExpresionName = (name + "_particle_exp")

	def query(self):
		if cmds.objExists(self.leadername):
			return 1
		else:
			return 0

	def create(self):
		if self.query():
			return self.leadername
		
		self.leader = cmds.curve(p=[(0, 0, 1.0), (0, 0.5, 0.866025), (0, 0.866025, 0.5), (0, 1, 0), 
		(0, 0.866025, -0.5), (0, 0.5, -0.866025), (0, 0, -1), (0, -0.5, -0.866025),
		(0, -0.866025, -0.5), (0, -1, 0), (0, -0.866025, 0.5), (0, -0.5, 0.866025), 
		(0, 0, 1), (0.707107, 0, 0.707107), (1, 0, 0), (0.707107, 0, -0.707107),
		(0, 0, -1), (-0.707107, 0, -0.707107), (-1, 0, 0), (-0.866025, 0.5, 0),
		(-0.5, 0.866025, 0), (0, 1, 0), (0.5, 0.866025, 0), (0.866025, 0.5, 0),
		(1, 0, 0), (0.866025, -0.5, 0), (0.5, -0.866025, 0), (0, -1, 0),
		(-0.5, -0.866025, 0), (-0.866025, -0.5, 0), (-1, 0, 0),
		(-0.707107, 0, 0.707107), (0, 0, 1)], d=1, n=self.leadername)

		# create button manipulator for easy keying - wish I could name or return a value from this
		cmds.buttonManip("cmds.setKeyframe(attribute='translate')", self.leader) 

		# Control parameters to the leader node	
		cmds.addAttr(self.leader, sn='stry', ln='stray', k=True) #, dv='posrand')
		cmds.addAttr(self.leader, sn='lf', ln="leaderFocus", k=True) #, dv='leaderfocus')
		cmds.addAttr(self.leader, sn='fo', ln='frameOffset', k=True) #, dv='frameoffset')
		cmds.addAttr(self.leader, sn='rnds', ln='randomness', k=True) #, dv=randomness)
		cmds.addAttr(self.leader, sn='pop', ln='population', k=True) #, dv=population)
		cmds.addAttr(self.leader, sn='shpe', ln='shape', dt="string") #, dv=population)

		cmds.addAttr(self.leader, ln="leaderMessage", dt="string", multi=True)
				
		self.editmotion()
		
		# clear selection to be safe
		cmds.select(cl=1)
		
		return self.leader
		
	def recordShape(self, shape):
		cmds.setAttr((self.leader + '.shpe'), str(shape), type="string")
		
	def select(self):
		if(cmds.objExists(self.leadername)):
			cmds.select(self.leadername)
			mel.eval("setToolTo $gMove")
		
	def editmotion(self):
		values = herds().values()

		# attach sliders
		cmds.setAttr((self.leadername + ".stray"), values["stray"])
		cmds.setAttr((self.leadername + ".frameOffset"), values["offset"])
		cmds.setAttr((self.leadername + ".leaderFocus"), values["focus"])
		cmds.setAttr((self.leadername + ".randomness"), values["randomness"])
	
	def followParticle(self):
		translateX = cmds.getAttr(self.leadername + ".tx") 
		translateY = cmds.getAttr(self.leadername + ".ty")
		translateZ = cmds.getAttr(self.leadername + ".tz") 

		self.leaderparticle = cmds.particle(p=(translateX, translateY, translateZ), n=self.leaderParticleName)
		cmds.xform(cp=True)

		self.leaderParticleExpression = cmds.expression(s=("vector $position= `getAttr " + self.leaderParticleName + ".position`;\n" +
			self.leadername + ".translateX = $position.x;\n" +
			self.leadername + ".translateY = $position.y;\n" +
			self.leadername + ".translateZ = $position.z;"), o=self.leadername, ae=1, uc="all", n=self.leaderParticleExpresionName)

	def deleteParticle(self):
		cmds.delete(self.leaderParticleName)
		cmds.delete(self.leaderParticleExpresionName)



# herds().ui()		
