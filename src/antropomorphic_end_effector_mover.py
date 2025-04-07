#!/usr/bin/env python3

import rospy
import numpy as np
from planar_3dof_control.msg import EndEffector
from geometry_msgs.msg import Vector3
from move_joints import JointMover
from rviz_marker import MarkerBasics
from ik_antropomorphic_arm import inverse_kinematics

class AntropomorphicEndEffectorMover:
    def __init__(self):
        rospy.init_node('antropomorphic_end_effector_mover')
        
        # Visualization markers
        self.marker_basics = MarkerBasics()
        self.goal_marker_index = 0
        self.actual_marker_index = 0  # Separate range for actual positions
        
        # Joint controller
        self.joint_mover = JointMover()
        
        # Initialize subscribers
        self.setup_subscribers()
                
        # Current state
        self.current_goal = None
        self.current_position = None
        self.elbow_config = "plus"  # Default elbow configuration
        
        rospy.loginfo("3DOF Arm Controller Ready")

    def setup_subscribers(self):
        """Initialize ROS subscribers with proper waiting"""
        # Goal position subscriber
        rospy.Subscriber("/ee_pose_commands", EndEffector, self.goal_callback)
        
        # Actual position subscriber
        rospy.Subscriber("/end_effector_real_pose", Vector3, self.position_callback)
        
        # Wait for initial messages
        rospy.loginfo("Waiting for initial messages...")
        rospy.wait_for_message("/ee_pose_commands", EndEffector)
        rospy.wait_for_message("/end_effector_real_pose", Vector3)
        rospy.loginfo("Initialization complete")

    def goal_callback(self, msg):
        """Process new end effector goal position"""
        self.current_goal = (msg.ee_xy_theta.x, msg.ee_xy_theta.y, msg.ee_xy_theta.z)
        self.elbow_config = msg.elbow_policy.data
        
        # Calculate inverse kinematics
        ik_results = inverse_kinematics(
            px=self.current_goal[0],
            py=self.current_goal[1],
            pz=self.current_goal[2],
            joint_limits=True
        )
        
        if ik_results['unreachable']:
            rospy.logwarn(f"Target unreachable: {self.current_goal}")
            return
            
        # Find solution matching our elbow configuration
        valid_solution = None
        for solution in ik_results['valid']:
            theta1, theta2, theta3, config = solution
            if config == self.elbow_config:
                valid_solution = (theta1, theta2, theta3)
                break
        
        if valid_solution:
            # Move joints to solution
            self.joint_mover.move_all_joints(*valid_solution)
            
            # Visualize goal (green sphere)
            self.marker_basics.publish_point(
                x=self.current_goal[0],
                y=self.current_goal[1],
                z=self.current_goal[2],
                index=self.goal_marker_index
            )
            self.goal_marker_index = (self.goal_marker_index + 1) 
        else:
            rospy.logwarn(f"No valid solution for {self.elbow_config} config at {self.current_goal}")

    def position_callback(self, msg):
        """Update and visualize actual end effector position"""
        self.current_position = (msg.x, msg.y, msg.z)
        
        # Visualize actual position (red sphere)
        self.marker_basics.publish_point(
            x=msg.x,
            y=msg.y,
            z=msg.z,
            index=self.actual_marker_index
        )
        self.actual_marker_index = (self.actual_marker_index + 1) 
        
        # Log position error if we have a current goal
        if self.current_goal:
            error = np.linalg.norm(np.array(self.current_position) - np.array(self.current_goal))
            rospy.logdebug(f"Position error: {error:.4f} m")

    def run(self):
        """Main control loop"""
        rate = rospy.Rate(10)  # 10Hz update rate
        while not rospy.is_shutdown():
            rate.sleep()

if __name__ == '__main__':
    try:
        controller = AntropomorphicEndEffectorMover()
        controller.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("Shutting down arm controller")