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


def reach(msg):
	status = rospy.get_param("/timer_srv_active")
	if status['p'] is True:
		print("timer active")
		curr_x = msg.pose.pose.position.x
		curr_y = msg.pose.pose.position.y
		print("curr_x: ",curr_x,", curr_y",curr_y,"\n")
		print("goal: %(",status['x'],"and",status['y'],") \n")
		if (curr_x == status['x']) and (curr_y == status['y']):
			print("goal reached!")
			rospy.set_param("/timer_srv_active",{'p': False, 'x': 0.0, 'y': 0.0})
			while(status['p'] is not False):
				status = rospy.get_param("/timer_srv_active")
	else:
		print("timer inactive")

def goal_reached():
	rospy.init_node('goal_reached')
	
	sub = rospy.Subscriber('/odom', Odometry, reach)
	
	rospy.spin()

if __name__ == "__main__":
	goal_reached()
