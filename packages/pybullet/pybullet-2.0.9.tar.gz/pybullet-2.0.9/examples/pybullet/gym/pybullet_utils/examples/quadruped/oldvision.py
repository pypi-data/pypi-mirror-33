import pybullet as p
import time
p.connect(p.GUI)
jointNames={}
jointNames[p.JOINT_REVOLUTE]="JOINT_REVOLUTE"
jointNames[p.JOINT_FIXED]="JOINT_FIXED"
p.setPhysicsEngineParameter(numSolverIterations=1000)
vision = p.loadURDF("oldnew.urdf",useFixedBase=True)

for j in range(p.getNumJoints(vision)):
	jointInfo = p.getJointInfo(vision,j)
	print("joint ",j," = ",jointInfo[1], "type=",jointNames[jointInfo[2]])
	p.setJointMotorControl2(vision,j,p.POSITION_CONTROL,force=10000)

motAid= p.addUserDebugParameter("motA",-1.5,1.5,0)
motBid= p.addUserDebugParameter("motB",-1.5,1.5,0)
motCid= p.addUserDebugParameter("motC",-1.5,1.5,0)

camTargetPos=[0.25,0.62,-0.15]
camDist = 1
camYaw = -2
camPitch=-16
p.resetDebugVisualizerCamera(camDist, camYaw, camPitch, camTargetPos)



p.setJointMotorControl2(vision,1,p.VELOCITY_CONTROL,targetVelocity=0,force=200)
p.setJointMotorControl2(vision,2,p.VELOCITY_CONTROL,targetVelocity=0.1,force=200)
p.setJointMotorControl2(vision,3,p.VELOCITY_CONTROL,targetVelocity=0, force=0)
p.setJointMotorControl2(vision,4,p.VELOCITY_CONTROL,targetVelocity=0, force=200)
#p.setJointMotorControl2(vision,5,p.VELOCITY_CONTROL,targetVelocity=0, force=0)
p.setJointMotorControl2(vision,6,p.VELOCITY_CONTROL,targetVelocity=0, force=0)
#p.setJointMotorControl2(vision,4,p.VELOCITY_CONTROL,targetVelocity=0, force=100)

c = p.createConstraint(vision,3,vision,4,jointType=p.JOINT_GEAR,jointAxis =[0,1,0],parentFramePosition=[0,0,0],childFramePosition=[0,0,0])
p.changeConstraint(c,gearRatio=-1, gearAuxLink = 1,maxForce=1000000)
#p.changeConstraint(c,gearRatio=-1,maxForce=1000000)

p.setRealTimeSimulation(1)
while (1):
	motA = p.readUserDebugParameter(motAid)
	motB = p.readUserDebugParameter(motBid)
	motC = p.readUserDebugParameter(motCid)

	p.setJointMotorControl2(vision,1,p.VELOCITY_CONTROL,targetVelocity=motA,force=200)
	p.setJointMotorControl2(vision,4,p.VELOCITY_CONTROL,targetVelocity=motB,force=200)
	p.setJointMotorControl2(vision,6,p.VELOCITY_CONTROL,targetVelocity=motC,force=200)

	p.setGravity(0,0,0)
	time.sleep(1./240.)

