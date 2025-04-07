#!/usr/bin/env python3

import numpy as np

def inverse_kinematics(px, py, pz, joint_limits=True):
    """
    Compute inverse kinematics for a 3-DOF arm with joint limits.
    Considers both positive and negative A cases for complete solution space.
    
    Args:
        px, py, pz: Target end-effector position
        joint_limits: Whether to enforce joint constraints
        
    Returns:
        {
            'valid': List of valid (theta1, theta2, theta3) solutions,
            'invalid': List of solutions violating joint limits,
            'unreachable': Bool if target is outside workspace
        }
    """
    # Joint limits (radians)
    theta2_min, theta2_max = -np.pi/4, 3*np.pi/4
    theta3_min, theta3_max = -3*np.pi/4, 3*np.pi/4

    results = {'valid': [], 'invalid': [], 'unreachable': False}

    # Consider both A+ and A- cases
    for A_sign in [1, -1]:
        A = A_sign * np.sqrt(px**2 + py**2)
        B = pz
        
        # Workspace check: enforce joint limits
        cos_theta3 = (A**2 + B**2 - 2)/2
        if abs(cos_theta3) > 1:
            results['unreachable'] = True
            continue

        # theta1 calculation (adjust for A- case)
        theta1 = np.arctan2(py, px)
        if A_sign < 0:
            theta1 = theta1 + np.pi if theta1 < 0 else theta1 - np.pi
        
        # Elbow solutions
        for theta3 in [np.arccos(cos_theta3), -np.arccos(cos_theta3)]:
            # Shoulder angle calculation
            C = 2 * (np.cos(theta3/2)**2)
            D = np.sin(theta3)
            theta2 = np.arctan2(B*C - A*D, A*C + B*D)

            # Check joint limits
            theta2_valid = theta2_min <= theta2 <= theta2_max
            theta3_valid = theta3_min <= theta3 <= theta3_max

            config = "plus-" if theta2 > 0 else "minus-"
            config += "plus" if theta3 > 0 else "minus"
            # config += 'A: plus' if A_sign > 0 else 'A: minus'
            candidate_solution = (theta1, theta2, theta3, config)

            if joint_limits:
                if theta2_valid and theta3_valid:
                    
                    results['valid'].append(candidate_solution)

                else:
                    results['invalid'].append(candidate_solution)
            else:
                results['valid'].append(candidate_solution)
    
    return results


if __name__ == "__main__":

    px, py, pz = 0.5, 0.6, 0.7
    results = inverse_kinematics(px, py, pz)
    
    print(f"Target position:\n\t({px}, {py}, {pz})")
    print("\nJoint limits:")
    print(f"\t-𝜋/4 ≤ 𝜃2 ≤ 3𝜋/4")
    print(f"\t-3𝜋/4 ≤ 𝜃3 ≤ 3𝜋/4")

    print("\nArm parameters:")
    print("\tDOF: 3")
    print("\tOffset: d1 = 0.0, d2 = 0.0, d3 = 0.0")
    print("\tRotation: alpha1: +90.0, alpha2: 0.0, alpha3: 0.0")
    print("\tArm lengths: r1 = 0.0, r2 = 1.0, r3 = 1.0")

    if results['unreachable']:
        print("Target is outside workspace!")
    else:
        print("\nVALID SOLUTIONS:")
        for i, (theta1, theta2, theta3, config) in enumerate(results['valid']):
            print(f"Solution {i+1} ({config}):")
            print(f"\ttheta1 = {np.degrees(theta1):.1f}° ({theta1:.4f} rad)")
            print(f"\ttheta2 = {np.degrees(theta2):.1f}° ({theta2:.4f} rad)")
            print(f"\ttheta3 = {np.degrees(theta3):.1f}° ({theta3:.4f} rad)")
        
        print("\nINVALID SOLUTIONS (violate joint limits):")
        for i, (theta1, theta2, theta3, config) in enumerate(results['invalid']):
            print(f"Solution {i+1} ({config}):")
            print(f"\ttheta1 = {np.degrees(theta1):.1f}° ({theta1:.4f} rad)")
            print(f"\ttheta2 = {np.degrees(theta2):.1f}° ({theta2:.4f} rad)") 
            print(f"\ttheta3 = {np.degrees(theta3):.1f}° ({theta3:.4f} rad)")
