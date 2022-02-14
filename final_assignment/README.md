Conents of the Assingment_3 Repository:
==========================================

The contents of this repository delve into my own solution for the 3rd graded assignment given to us in the Research Track class of the Robotics Engineering Master course held in Università degli Studi di Genova. The simulator I used has been provided to us by our professor, so if you are interested in the explaination of all its functionalities or want to know more about ROS, follow the specifications listed in """ [CarmineD8's Github Repository](https://github.com/CarmineD8/final_assignment) """.

Installing and running this code:
------------------------------------

To run this code, make sure you have installed ROS, then create your own workspace. Inside your new workspace, create a folder named "src", then clone all the contents of the package """ [slam_gmapping](https://github.com/CarmineD8/slam_gmapping) """ in it. Finally, you must do the same with the contents of this repository, putting the final_assignment package in your src folder. Both operations require the use the command:  
> `git clone url`

where "url" is the link to this repository. After that, go in the root of your acquired workspace with the command "cd correct_path/my_ws" (where correct_path is your specific path to the workspace) and run the commands:  
> `catkin_make` and `rospack profile`

You also need to make sure to have the "ros navigation stack" installed. If you don't, run the command:  
> `Apt-get install ros-<your_ros_distro>-navigation`

where "your_ros_distro" must correspond to your ros distribution version.

As the last step, type "cd src/final_assignment" in your previously opened shell, split it in 2 separate shells, then write the commands:  
> `roscore &` and then `roslaunch sim_base.launch` (on the first shell)  
> `roslaunch final_assignment.launch` (on the second shell)

If you haven't downloaded Ros, you can do it by following the instuctions listed in """ [ROS Wiki](https://wiki.ros.org) """.  

Note: if not already present, add the line "source /opt/ros/noetic/setup.bash" to your .bashrc file using the command:  
> `gedit .bashrc`  
Also, add the line "source /correct_path/my_ws/devel/setup.bash", where correct_path is your specific path to the workspace.

For other useful info on the simulator used to produce this code, or the installation of the components required to make it work, you can always refer to the original repository granted to us by our professor. The link to his repositories has been already given in the previous paragraph.

## Objectives and Useful Info:

The code produced for this assignment is contained in "my_ws/src", specifically in the folders ... and has been carried out in ROS. Other than that, we produced this README to explain its contents.  
The core of the assignment was:  
> Develop a software architecture for the control of the robot in the environment, that should be able to get the user request, and let the robot execute one of the following behaviors:  
> 1) autonomously reach a x,y coordinate inserted by the user;  
> 2) let the user drive the robot with the keyboard;  
> 3) let the user drive the robot assisting them to avoid collisions (the robot: should not go forward if there is an obstacle in the front; should not turn left/right if there are obstacles on the left/right);  
> 4) optional: you can directly use actions, as seen in class; the user can also enter a target that is not reachable, thus you can implement your own timeout, to cancel the goal if the request cannot be accomplished; also give the user the possibility of cancelling the goal.

The code produced handles all 3 points of the assignment without any problems and also takcles some of the optional tasks given to us. I implemented six nodes, that must work concurrently to achieve our objectives.  

One node (userinterface, defined in the user.py script) handles the user interface, allowing the user to change the working modality (state) of the program if he/she wishes to use a different function (it will also alert the user in case something goes wrong or the goal he/she chooses falls outside the map). One node (goal_server, included in goal_service.py) handles the setting of goals and the optional feature that allows the user cancel them. Two other nodes handle the timing aspect (goal_reached and timer_server, respectively included in goal_reached.py and my_timer.py) for the opitonal feature to cancel the goal if it has not been reached before a certain timeout, and the two final nodes (tele_ctrl_active, included in tele_control.py and teleop_srv_active, included in teleservice.py) handle the movement control by the user and the assistance to avoid collisions, if required by the user.  

Thus, the only optional feature not included is the use of actions. Also, while it was suggested to use teleop_twist_keyboard to handle the user motion control over the robot, to avoid having to make a new node from scratch, I preferred to use my own node and structure, for clarity. Both these unincluded points will be discussed in the "Possible Improvements" section of this paper, together with some specific considerations on movement control.  

Regarding the actual nodes, to work together they obviously need to pass informations to eachother. To do it in an efficient way, we used the "ROS Parameter Server", which allowed us to specify some parameters of interest which would be available to all nodes both for writing and reading at each time instant. This allowed us to avoid having to define custom services or messages, granted to all nodes the possibility to always know which other nodes are active and which modality has been selected, and made the code much more compact. We used these parameters to "set nodes to active or unactive states" whenever the user (or another active node) requested so, and also to pass "starting parameters" of interest for setting up correctly each functionality when called. However, this method doesn't ensure synchronicity! Thus: we had to avoid using ROSparameters for values that would change too quickly or often; we had to make sure that nodes would be well coordinated; we had to prevent the user and the active nodes from overwriting (setting) the same parameters while they are being registered (that would break the correctness of the requested sequence of actions). To do these things, we used the principle of "busy waiting": each time a crucial parameter is set to trigger a state change in the process (particularly when some nodes need to be stopped in order for others to become active), we wait before proceeding until we are certain that the change has been registered, by simply checking for the parameter's values in loop until they get changed into what they should be (meanwhile we also stop the robot from moving, to avoid funny behaviours). This is a security measure that's probably not entirely necessary, since the change in the parameter server happens very quickly, but it ensures more safety in the program's behaviour (explained in detail in the following section).

### Code Behaviour (pseudocode):

The main part of the user.py code handles the user interface which will exchange messages with the user through the terminal, to allow him/her to decide what functionality to use to influence the robot's behaviour among those available. It does so by doing the following things:

- initialize the node
- set itself as a publisher for /cmd_vel
- Set "velocity" and "goalactive" to 0
- while looping:  
___Print a message for the user, asking which mode to use  
___Set choice to user input  
___Get teleop_srv_active rosparameter and Set tcheck and gcheck to them  

___If choice is 1:  
_____Set teleop_srv_active rosparameter permission to False and control to False  
_____While rosparameters aren't set:  
_______Publish velocity (to stop the robot) and get rosparameters  
_____Set x and y to user input  
_____If x and y are outside the map limitations:  
_______print a message for the user, asking if he/she wants to continue regardless  
_______Get user input  
_______If input is 'y':  
_________Set goal_srv_active rosparameter permission to 1, goal_x to x and goal_y to y  
_________Set goalactive to 1  
_______Else:  
_________do nothing  
_____Else:  
_______Set goal_srv_active rosparameter permission to 1, goal_x to x and goal_y to y  
_______Set goalactive to 1  

___Else if choice is 2:  
_____If goalactive is 1:  
_______Set teleop_srv_active rosparameter permission to False and control to False  
_______While rosparameters aren't set:  
_________Publish velocity (to stop the robot) and get rosparameters  
_______Set goal_srv_active rosparameter permission to 2, goal_x to 0 and goal_y to 0  
_______Set goalactive to 0  
_____Else:  
_______do nothing  

___Else if choice is 3:  
_____Set goal_srv_active rosparameter permission to 2, goal_x to 0 and goal_y to 0  
_____While rosparameters aren't set:  
_______Publish velocity (to stop the robot) and get rosparameters  
_____Set teleop_srv_active rosparameter permission to True and control to False  
_____Set goalactive to 0  

___Else if choice is 4:  
_____Set goal_srv_active rosparameter permission to 2, goal_x to 0 and goal_y to 0  
_____While rosparameters aren't set:  
_______Publish velocity (to stop the robot) and get rosparameters  
_____Set teleop_srv_active rosparameter permission to True and control to True  
_____Set goalactive to 0  

___Else:
_____do nothing  

The goal_service.py code handles the option to set a new goal but also the option to cancel it. These two functionalities are expressed through two different functions: set_goal and cancel_goal. Before discussing those, we will discuss the main:

- initialize the node
- Set itself as a publisher for /move_base/goal and /move_base/cancel
- Set cnt to 0 (incremental counter used to give different ids to each goal set)
- While looping:  
___Get goal_srv_active  
___If goal_srv_active permission is 1:  
_____Set cnt to set_goal's returned value, giving it also as argument to set_goal  
___Else if goal_srv_active permission is 2:  
_____Call cancel_goal, passing cnt as argument  

Functions of goal_service.py:

- cancel_goal:  
___publish cnt as a GoalID msg on /move_base/cancel  
___Set goal_srv_active rosparameter permission to 0, goal_x to 0 and goal_y to 0  
___Set timer_srv_active rosparameter permission to False, x to 0 y to 0  

- set_goal:  
___increase cnt by 1  
___Define Goal as a MoveBaseActionGoal msg  
___Set Goal id to cnt, frame_id to "map", orientation.w to 1, position.x to x and position.y to y  
___publish Goal on /move_base/goal  
___Set timer_srv_active rosparameter permission to True, x to x, y to y  
___Set goal_srv_active rosparameter permission to 0, goal_x to x and goal_y to y  
___return cnt  

The goal_reached.py code is necessary to my_timer.py because it aims at informing the timer when the goal has been reached, to stop the timer and avoid unnecessary cancellings of the goal due to timeout. It is a subscriber node based on the callback reach. It's main is straightforward:

- initialize the node
- subscribe to /odom using the callback reach
- spin

Callback of goal_reached.py:

- reach:  
___Get timer_srv_active rosparameter and set status to it  
___If status permission is True:  
_____Set curr_x to msg position.x and curr_y to msg position.y  
_____If curr_x is equal to status x and curr_y is equal to status y:  
_______Set timer_srv_active rosparameter permission to False, x to 0, y to 0  
_______while rosparameters aren't set:  
_________Get timer_srv_active rosparameter and set status to it  
___Else:  
_____do nothing  

The my_timer.py code handles the task of cancelling the goal if it is taking too much time to be reached (it happens when the goal falls outside the map) thanks to a preset timeout (depending on specific needs it can be changed: now it's set at 300 seconds, thus 5 minutes). Here we describe only it's main since it doesn't have extra functions:

- initialize the node
- While looping:  
___Get timer_srv_active rosparameter and set status to it  
___Set start to 0, end to 0 and timeout to 300  
___If status permission is True:  
_____Set start to current time  
___While status permission is True:  
_____Set end to current time  
_____If end minus start is greater than timeout:  
_______Set goal_srv_active rosparameter permission to 2, goal_x to 0, goal_y to 0  
_______Set timer_srv_active rosparameter permission to False, x to 0, y to 0  
_______Set start to end  
_____Get timer_srv_active rosparameter and set status to it  

The teleservice.py code handles the task of allowing the user to give inputs aimed at controlling the robot in its movement. If the user chose the unassisted modality (mode 3) only this node will be involved, otherwise this node will be assisted by the tele_control node. Teleservice uses a function called move, that will be described after its main description:

- initialize the node
- Set cnt to 0 and correct to False
- While looping:  
___Get teleop_srv_active rosparameter and set tcheck to it  
___If tcheck permission is True:  
_____print a message to the user  
_____Set choice to the user input  
_____If choice is between 1 and 9:  
_______Set cnt to 0 and correct to True  
_____Else:  
_______Set correct to False  
___Get teleop_srv_active rosparameter and set tcheck to it (again, since the user could waste an arbitrary ammount of time before answering)  
___If tcheck permission is True and tcheck control is True and correct is True:  
_____Set correct to False  
_____Call move, giving it choice and 1 as arguments  
___Else if tcheck permission is True and tcheck control is False and correct is True:  
_____Set tele_ctrl_active rosparameter permission to False, linear to 0 and angular to 0  
_____Get tele_ctrl_active rosparameter and set check to it  
_____While check permission is True:  
_______Get tele_ctrl_active rosparameter and set check to it  
_____Set correct to False  
_____Call move, giving it choice and 2 as arguments  
___Else if cnt is equal to 0:  
_____Set tele_ctrl_active rosparameter permission to False, linear to 0 and angular to 0  
_____Get tele_ctrl_active rosparameter and set check to it  
_____While check permission is True:  
_______Get tele_ctrl_active rosparameter and set check to it  
_____Print a message for the user  
_____Set cnt to 1 ()  

Function of teleservice.py:

- move(num,job):
___Set vel as a Twist type msg  
___If num is equal to 1, 2 or 3:  
_____Set vel.linear.x to 0.3  
___Else if num is equal to 4, 5 or 6:  
_____Set vel.linear.x to 0.0  
___Else:  
_____Set vel.linear.x to -0.3  

___If num is equal to 3, 6 or 9:  
_____Set vel.angular.z to 0.3  
___Else if num is equal to 2, 5 or 8:  
_____Set vel.angular.z to 0.0  
___Else:  
_____Set vel.angular.z to -0.3  

___If job is equal to 1:  
_____Set tele_ctrl_active rosparameter permission to True, linear to vel.linear.x and angular to vel.angular.z  
_____Get tele_ctrl_active rosparameter and set check to it  
_____While check permission is not True:  
_______Get tele_ctrl_active rosparameter and set check to it  
___Else if job is equal to 2:  
_____publish vel on /cmd_vel  
___Else:  
_____do nothing  

The tele_control.py code handles the task of assisting the movement at the user's request. It acts as a proxy between the teleservice node and /cmd_vel, because it checks the values that teleservice wants to publish before they are published, to modify them if necessary. It is a subscriber node that uses the outputs of the robot's laser scanner to avoid crashing into obstacles. Its main just handles the initialization of the node and the subscription to /scan, thus we will directly describe its callback (LaserCallback):

- LaserCallback:  
___Get tele_ctrl_active rosparameter and set info to it  
___Get teleop_srv_active rosparameter and set telecheck to it  
___If telecheck permission is True and telecheck control is True and info permission is True:  
_____Define regions as a list with arguments "right; fright; front; fleft left" and Set each argument to the minimum obstacle distances among those perceived by /scan in those specific regions  
_____Set vel as a Twist type msg  
_____Set vel.linear.x to info linear and vel.angular.z to info angular  
_____Check vel.linear.x and vel.angular.z to understand which mode the user wants among "front, fsx, fdx, stop, turndx, turnsx, bwds"  
_____Set left to the minimum among regions fleft and regions left  
_____Set right to the minimum among regions fright and regions right  
_____Set threshold to 1  
_____Check whether the distance perceived in the region corresponding to the mode currently selected is lower than threshold  
_______Set vel.linear.x and vel.angular.z accordingly, to avoid obstacles  
_____publish vel on /cmd_vel  

#### Possible Improvements:

In this section, we will discuss the main improvements that could be made to our code: 

- the first one, regarding optional and suggested features: we could have used actions to boost the efficiency of the code, but this would need considerable modifications on the code; instead of using a custom node we could have directly used teleop_twist_keyboard to give control of the robot to the user (as suggested) by simply remapping the output of that node to a custom one from the launch file (no changes needed to it), whose job would be to control it before sending it to cmd_vel. However, there is a reason we chose not to use teleop: if we did use it without changing anything, its interface would have been active and available to the user since the start of the program. But since, theoretically, the goal of the assignment was to have a custom user interface that allows the user to choose between different functionalities, it would have been counterintuitive to have one functionality always available from the start and separate in its usw from the main user interface. To improve on this, we would have had to modify the teleop node in order to make it unavailable to the user at the start or while other functionalities were being used. But that would defeat the point of using teleop entirely, since it was suggested to use it without any modifications, to avoid having to create a custom node and make unnecessary extra work! Thus, from a design perspective, we opted to avoid using it. However, since teleop is certainly a more powerful tool than our custom node, it would be an improvement to incorporate it in some way regardless.  

- the second one, regarding movement assistance: the robot is aided in movement by continuous checks on the distance of nearby obstacles perceived by its laser scanners. Thus, it uses a threshold to determine if an obstacle is near or not and how to handle it. However, the threshold chosen may not be the best, depending on specific needs, thus it would be better to try and change it to get to a perfect behaviour. Also, to make sure the robot doesn't get stuck at angles or when surrounded, we opted for it to always turn in one specific direction when it finds itself in one of those situations. It would be better to come up with a way for the robot to reliably know where it's best to turn in these situations.  

- the third one, regarding speed: Even if only by little, using parameters from the ROS parameter server slows the program and reduces temporal efficiency due to its lack of synchronicity. This is not a problem when few processes are running (you can barely notice any difference with our program), but inside a more complex system it might still be problematic. Thus, a different and more complex solution may be taken into consideration for specific needs (perharps using actions, linking this possible improvement to the first one). 






