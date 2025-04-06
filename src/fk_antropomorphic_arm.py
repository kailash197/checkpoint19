#!/usr/bin/env python3
from generate_matrices import DHMatrixGenerator
from sympy import pi  

if __name__ == "__main__":
    # Ask theta from user
    theta1 = float(input("Enter the value for theta_1: "))
    theta2 = float(input("Enter the value for theta_2: "))
    theta3 = float(input("Enter the value for theta_3: "))

    # From checkpoint
    chain_length = 3
    matrices_to_simplify = ["A01", "A12", "A23", "A03"]
    save_simplified_matrices = ["A03"]
    
    # Use LaTeX-compatible symbols
    substitutions = {
        "A01": {'alpha': pi/2, 'r': 0.0, 'd': 0.0, 'theta': theta1},
        "A12": {'alpha':0.0, 'r': 1.0, 'd': 0.0, 'theta': theta2},
        "A23": {'alpha':0.0, 'r': 1.0, 'd': 0.0, 'theta': theta3}
    }
    
    # Initialize and process
    dh = DHMatrixGenerator()
    matrix_names = dh.generate_chain(chain_length)
    dh.create_matrices(matrix_names)
    dh.apply_substitutions(substitutions)
    dh.build_compound_matrices(chain_length)
    dh.simplify_matrices(matrices_to_simplify)
    dh.save_matrices(save_simplified_matrices, simplified=True, postfix="_simplify_evaluated")

    # Extract position (last column, first 3 rows)
    tf_matrix = dh.get_matrix("A03", simplified=True)
    position = tf_matrix[:3, 3]
    orientation = tf_matrix[:3, :3]
    print("Position Matrix: ")
    print(position)
    
    print("\nOrientation Matrix: ")
    print(orientation)

    # END OF PROGRAM
