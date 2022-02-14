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


def timer_client():
	rospy.init_node('timer_server')
	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
		status = rospy.get_param("/timer_srv_active")
		print("reset \n")
		start = 0.0
		end = 0.0
		timeout = 300.0
		if status['p'] is True:
			print("start \n")
			start = time.perf_counter()
		while(status['p'] is True) :
			end = time.perf_counter()
			if (end - start) > timeout: 
				print("timeout \n")
				rospy.set_param("/goal_srv_active",{'p': 2, 'goal_x': 0., 'goal_y': 0.})
				rospy.set_param("/timer_srv_active",{'p': False, 'x': 0.0, 'y': 0.0})
				start = end #reset
			status = rospy.get_param("/timer_srv_active")
		
		rate.sleep()

if __name__ == "__main__":
	timer_client()
