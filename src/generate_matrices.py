#!/usr/bin/env python3

from sympy import Matrix, cos, sin, Symbol, simplify, trigsimp, pi, symbols
from sympy.interactive import printing
from typing import List, Dict, Optional, Union
from functools import reduce

class DHMatrixGenerator:
    def __init__(self):
        """Initialize the DH matrix generator"""
        printing.init_printing(use_latex=True)
        self.generic_matrix = None
        self.matrices = {}  # Stores all created matrices
        self.simplified_matrices = {}  # Stores simplified versions
        self._create_generic_matrix()

    def _create_generic_matrix(self):
        """Create and simplify the generic DH matrix"""
        theta_i = Symbol("theta_i")
        alpha_i = Symbol("alpha_i")
        r_i = Symbol("r_i")
        d_i = Symbol("d_i")
        
        self.generic_matrix = simplify(Matrix([
            [cos(theta_i), -sin(theta_i)*cos(alpha_i), 
             sin(theta_i)*sin(alpha_i), r_i*cos(theta_i)],
            [sin(theta_i), cos(theta_i)*cos(alpha_i), 
             -cos(theta_i)*sin(alpha_i), r_i*sin(theta_i)],
            [0, sin(alpha_i), cos(alpha_i), d_i],
            [0, 0, 0, 1]
        ]))

    def generate_chain(self, chain_length: int):
        """Generate standard matrix names for a kinematic chain"""
        matrix_names = []
        for i in range(chain_length):
            matrix_names.append(f"A{i}{i+1}")
        for i in range(2, chain_length+1):
            matrix_names.append(f"A0{i}")
        return matrix_names

    def create_matrices(self, matrix_names: List[str]):
        """Initialize matrix containers"""
        for name in matrix_names:
            self.matrices[name] = None
            self.simplified_matrices[name] = None

    def apply_substitutions(self, substitutions: Dict[str, Dict[str, Union[float, Symbol]]]):
        """Apply DH parameter substitutions to specified matrices"""
        for matrix_name, params in substitutions.items():
            if matrix_name not in self.matrices:
                raise ValueError(f"Matrix {matrix_name} not initialized")
            
            # Create LaTeX-compatible symbols
            default_theta = Symbol(f"theta_{matrix_name[2:]}")
            default_alpha= Symbol(f"alpha_{matrix_name[2:]}")
            default_d = Symbol(f"d_{matrix_name[2:]}")
            default_r =Symbol(f"r_{matrix_name[2:]}")

            # Create substitution dictionary or use default
            subs_dict = {
                Symbol("alpha_i"): params.get('alpha', default_alpha),
                Symbol("r_i"): params.get('r', default_r ),
                Symbol("d_i"): params.get('d', default_d),
                Symbol("theta_i"): params.get('theta', default_theta)
            }
            
            self.matrices[matrix_name] = self.generic_matrix.subs(subs_dict)

    def build_compound_matrices(self, chain_length: int):
        """Automatically build compound matrices (A02, A03, etc.)"""
        for i in range(2, chain_length+1):
            matrix_name = f"A0{i}"
            if matrix_name in self.matrices:
                # Multiply individual matrices to form compound matrix
                matrices_to_multiply = []
                for j in range(i):
                    individual_name = f"A{j}{j+1}"
                    if individual_name in self.matrices and self.matrices[individual_name] is not None:
                        matrices_to_multiply.append(self.matrices[individual_name])
                
                if matrices_to_multiply:
                    self.matrices[matrix_name] = reduce(lambda a, b: a * b, matrices_to_multiply)

    def simplify_matrices(self, matrix_names: List[str]):
        """Simplify specified matrices"""
        for name in matrix_names:
            if name in self.matrices and self.matrices[name] is not None:
                self.simplified_matrices[name] = trigsimp(self.matrices[name])

    def save_matrices(self, matrix_names: List[str], simplified=False, prefix: str = ""):
        """Save specified matrices to files with proper LaTeX escaping"""
        from sympy import preview
        
        for name in matrix_names:        
            if simplified:
                if name in self.simplified_matrices and self.simplified_matrices[name] is not None:
                    matrix = self.simplified_matrices.get(name)
                    preview(matrix, viewer='file', filename=f"{prefix}{name}_simplify.png", dvioptions=['-D','300'])
            else:
                if name in self.matrices and self.matrices[name] is not None:
                    matrix = self.matrices.get(name)                
                    preview(matrix, viewer='file', filename=f"{prefix}{name}.png", dvioptions=['-D','300'])


def main():
    # User provides these inputs:
    chain_length = 3
    matrices_to_simplify = ["A01", "A12", "A23", "A03"]
    save_matrices = ["A01", "A12", "A23", "A03"]
    save_simplified_matrices = ["A03"]
    
    # Use LaTeX-compatible symbols
    substitutions = {
        "A01": {'alpha': pi/2, 'r': 0.0, 'd': 0.0},
        "A12": {'alpha':0.0, 'd': 0.0},
        "A23": {'alpha':0.0, 'd': 0.0}
    }
    
    # Initialize and process
    dh = DHMatrixGenerator()
    matrix_names = dh.generate_chain(chain_length)
    dh.create_matrices(matrix_names)
    dh.apply_substitutions(substitutions)
    dh.build_compound_matrices(chain_length)
    dh.simplify_matrices(matrices_to_simplify)
    dh.save_matrices(save_matrices)
    dh.save_matrices(save_simplified_matrices, simplified=True)

if __name__ == "__main__":
    main()