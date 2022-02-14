#!/usr/bin/env python

#you have to put the py code in a folder called "scripts" in the pkg and you need to make it executable with chmod +x to make it work -> you don't need to build it. Type ^C to kill it.
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty
import time
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseActionFeedback
from actionlib_msgs.msg import GoalID
from move_base_msgs.msg import MoveBaseActionGoal
from move_base_msgs.msg import MoveBaseActionFeedback
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

pub = rospy.Publisher('move_base/goal', MoveBaseActionGoal, queue_size=1)
pubc = rospy.Publisher('move_base/cancel', GoalID, queue_size=1000)

def cancel_goal(cnt):
	print("cancel with cnt: \n")
	print(cnt)
	print("cancel goal with id: \n")
	C_cmd = GoalID()
	C_cmd.id = str(cnt)
	print(str(cnt))
	pubc.publish(C_cmd)
	rospy.set_param("/goal_srv_active",{'p': 0, 'goal_x': 0., 'goal_y': 0.})
	rospy.set_param("/timer_srv_active",{'p': False, 'x': 0.0, 'y': 0.0})
	
def set_goal(x,y,cnt):
	print("setgoal with cnt: \n")
	cnt+=1
	print(cnt)
	Goal=MoveBaseActionGoal()
	print("create goal with id: \n")
	print(str(cnt))
	Goal.goal_id.id = str(cnt)
	Goal.goal.target_pose.header.frame_id = "map" 
	Goal.goal.target_pose.pose.orientation.w = 1.0 
	Goal.goal.target_pose.pose.position.x = x 
	Goal.goal.target_pose.pose.position.y = y
	pub.publish(Goal)
	rospy.set_param("/timer_srv_active",{'p': True, 'x': x, 'y': y})
	rospy.set_param("/goal_srv_active",{'p': 0, 'goal_x': x, 'goal_y': y})
	return cnt

def goal_server():
	rospy.init_node('goal_server')
	
	rate = rospy.Rate(10)
	cnt = 0
	while not rospy.is_shutdown():
		goal_param=rospy.get_param("/goal_srv_active")
		if goal_param['p'] == 1:
			print("permission 1 \n")
			cnt = set_goal(goal_param['goal_x'],goal_param['goal_y'],cnt)
		elif goal_param['p'] == 2:
			print("permission 2 \n")
			cancel_goal(cnt)
	
		rate.sleep()

if __name__ == "__main__":
	goal_server()
