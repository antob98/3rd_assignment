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

def LaserCallback(msg):
    info = rospy.get_param("/tele_ctrl_active")
    telecheck = rospy.get_param("/teleop_srv_active")
    if (telecheck['p'] is True) and (telecheck['control'] is True) and (info['p'] is True):
        regions = {
            'right': min(msg.ranges[0:143]),
            'fright': min(msg.ranges[144:287]),
            'front': min(msg.ranges[288:431]),
            'fleft': min(msg.ranges[432:575]),
            'left': min(msg.ranges[576:719])
        }
        
        vel = Twist()
        vel.linear.x = info['linear']
        vel.angular.z = info['angular']
        
        if vel.linear.x > 0 and vel.angular.z == 0:
            mode = 'front'
            print("command: 2")
        elif vel.linear.x > 0 and vel.angular.z < 0:
            mode = 'fsx'
            print("command: 1")
        elif vel.linear.x > 0 and vel.angular.z > 0:
            mode = 'fdx'
            print("command: 3")
        elif vel.linear.x == 0 and vel.angular.z == 0:
            mode = 'stop'
            print("command: 5")
        elif vel.linear.x == 0 and vel.angular.z > 0:
            mode = 'turndx'
            print("command: 6")
        elif vel.linear.x == 0 and vel.angular.z < 0:
            mode = 'turnsx'
            print("command: 4")
        else:
            mode = 'bwds'
            print("command: 7, 8 or 9")
        
        left = min(regions['fleft'],regions['left'])
        right = min(regions['fright'],regions['right'])
        
        threshold = 1.0 #may be too much: try between 0.5 and 1.0
        
        if mode == 'front' and (regions['front'] < threshold):
            vel.linear.x = 0
            vel.angular.z = 1.0
                                
        elif mode == 'fsx' and (regions['fleft'] < threshold):
            if (regions['front'] < threshold):
                if (left < threshold):
                    vel.linear.x = 0
                    vel.angular.z = 0.5
                else:
                    vel.linear.x = 0
                    vel.angular.z = -0.5
            else:
                vel.linear.x = 0.5
                vel.angular.z = 0
        elif mode == 'fdx' and (regions['fright'] < threshold):
            if (regions['front'] < threshold):
                if (right < threshold):
                    vel.linear.x = 0
                    vel.angular.z = -0.5
                else:
                    vel.linear.x = 0
                    vel.angular.z = 0.5
            else:
                vel.linear.x = 0.5
                vel.angular.z = 0
        
        elif (mode == 'turndx') and (right < threshold):
            vel.linear.x = 0
            vel.angular.z = -0.5
        elif (mode == 'turnsx') and (left < threshold):
            vel.linear.x = 0
            vel.angular.z = 0.5
            
        pub.publish(vel)



def tele_control():
	rospy.init_node('tele_control')
	
	sub = rospy.Subscriber('/scan', LaserScan, LaserCallback)
	
	rospy.spin()
		
if __name__ == "__main__":
	tele_control()
	
	

