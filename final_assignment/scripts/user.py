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

pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)


def userinterface():
	rospy.init_node('userinterface') 
	rate = rospy.Rate(10)
	vel=Twist()
	vel.linear.x=0.0
	vel.angular.z=0.0
	g_active = 0
	while not rospy.is_shutdown():
		rospy.loginfo("hi user, please write '1' if you want to manually set a target goal and let the robot autonomously reach it, '2' if you want to cancel a previous goal, '3' if you want ..., or '4' if you want...: \n")
		choice=int(input("input the number: "))
		
		tcheck = rospy.get_param("/teleop_srv_active")
		gcheck = rospy.get_param("/goal_srv_active")
		print("you have selected choice: ",choice)
		print("loading...")
		if choice == 1:
			rospy.set_param("/teleop_srv_active",{'p': False, 'control': False})
			while((tcheck['p'] is not False) or (tcheck['control'] is not False)):
				pub.publish(vel)
				tcheck = rospy.get_param("/teleop_srv_active")
				gcheck = rospy.get_param("/goal_srv_active")
			x=float(input("input the x coordinate of your target goal: \n"))
			y=float(input("input the y coordinate of your target goal: \n"))
			if ((x<-7.8) or ((x<-2) and (y<-7.2)) or (y<-10) or (x>3.8) or (y>6.5) or ((y>0.5) and (x>1)) or ((x>-1.8) and (x< 1) and (y>-2.25))):
				print("your goal may fall outside the map...")
				omap=input("do you still want to send it? y/n (a wrong input will be counted as 'n') \n")
				if(omap == 'y'):
					rospy.set_param("/goal_srv_active",{'p': 1, 'goal_x': x, 'goal_y': y})
					g_active = 1
				else:
					print("gotcha! \n")
			else:
				rospy.set_param("/goal_srv_active",{'p': 1, 'goal_x': x, 'goal_y': y})
				g_active = 1
			
		elif choice == 2:
			if g_active == 1:
				rospy.set_param("/teleop_srv_active",{'p': False, 'control': False})
				while((tcheck['p'] is not False) or (tcheck['control'] is not False)):
					pub.publish(vel)
					tcheck = rospy.get_param("/teleop_srv_active")
				rospy.set_param("/goal_srv_active",{'p': 2, 'goal_x': 0., 'goal_y': 0.})
				g_active = 0
			else:
				print("there's no currently active goal! \n")
			
		elif choice == 3:
			rospy.set_param("/goal_srv_active",{'p': 2, 'goal_x': 0., 'goal_y': 0.})
			while(gcheck['p'] != 2):
				pub.publish(vel)
				gcheck = rospy.get_param("/goal_srv_active")
			rospy.set_param("/teleop_srv_active",{'p': True, 'control': False})
			g_active = 0
			
		elif choice == 4:
			rospy.set_param("/goal_srv_active",{'p': 2, 'goal_x': 0., 'goal_y': 0.})
			while(gcheck['p'] != 2):
				pub.publish(vel)
				gcheck = rospy.get_param("/goal_srv_active")
			rospy.set_param("/teleop_srv_active",{'p': True, 'control': True})
			g_active = 0
			
		else:
			rospy.loginfo("wrong input! try again. \n")
		
		rate.sleep()
		

if __name__ == '__main__':
	try:
		userinterface()
	except rospy.ROSInterruptException:
		pass
		

