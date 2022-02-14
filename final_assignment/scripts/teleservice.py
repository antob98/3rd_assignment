#!/usr/bin/env python

#you have to put the py code in a folder called "scripts" in the pkg and you need to make it executable with chmod +x to make it work -> you don't need to build it. Type ^C to kill it.
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty 
import time
from move_base_msgs.msg import MoveBaseActionGoal
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

msg = """
hi user, please follow the following button chart to move the robot in the corresponding direction:
------------------
Moving around:
   1    2    3
   4    5    6
   7    8    9
------------------

Note: If you are in controlled mode, consider that backwards motion won't be controlled!

CTRL-C to quit
"""

passive_msg = """
STOP: The Node is unactive or has been deactivated! Any given input will be discarded. 
Waiting for activation...
"""

pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)


def move(num,job):
	vel = Twist()
	if (num == 1) or (num == 2) or (num ==3):
		vel.linear.x = 0.3
	elif (num == 4) or (num == 5) or (num ==6):
		vel.linear.x = 0.0
	else:
		vel.linear.x = -0.3
	
	if (num == 3) or (num == 6) or (num ==9):
		vel.angular.z = 0.3
	elif (num == 2) or (num == 5) or (num ==8):
		vel.angular.z = 0.0
	else:
		vel.angular.z = -0.3
	
	if (job == 1):
		rospy.set_param("/tele_ctrl_active",{'p': True, 'linear': vel.linear.x, 'angular': vel.angular.z})
		check = rospy.get_param("/tele_ctrl_active")
		while(check['p'] is not True):
			check = rospy.get_param("/tele_ctrl_active")
	elif(job == 2):
		pub.publish(vel)
	else:
		print("an error has occurred!")
	

def tele_srv():
	rospy.init_node('tele_srv')
	rate = rospy.Rate(10)
	cnt = 0
	correct = False
	while not rospy.is_shutdown():
		tcheck = rospy.get_param("/teleop_srv_active")
		if (tcheck['p'] is True):
			print(str(msg))
			choice=int(input("input the number: "))
			if (choice >= 1) and (choice <= 9):
				cnt = 0
				correct = True
			else:
				print("wrong input!")
				correct = False
		tcheck = rospy.get_param("/teleop_srv_active")
		if (tcheck['p'] is True) and (tcheck['control'] is True) and (correct is True):
			print("tele + control \n")
			correct = False
			move(choice,1)
		elif (tcheck['p'] is True) and (tcheck['control'] is False) and (correct is True):
			rospy.set_param("/tele_ctrl_active",{'p': False, 'linear': 0.0, 'angular': 0.0})
			check = rospy.get_param("/tele_ctrl_active")
			while(check['p'] is True):
				check = rospy.get_param("/tele_ctrl_active")
			print("tele \n")
			correct = False
			move(choice,2)
		elif cnt == 0:
			rospy.set_param("/tele_ctrl_active",{'p': False, 'linear': 0.0, 'angular': 0.0})
			check = rospy.get_param("/tele_ctrl_active")
			while(check['p'] is True):
				check = rospy.get_param("/tele_ctrl_active")
			print(str(passive_msg))
			cnt = 1
		rate.sleep()
		
if __name__ == "__main__":
	tele_srv()
