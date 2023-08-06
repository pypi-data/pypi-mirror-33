import math
from .Generalmatrix import matrix
    
class matrix2by2(matrix):
    """Two by Two square matrix class for instantiating
    2x2 square matrices and performing operations on them.
    
    Attributes:
        row_size(int) representing the number of rows in matrix
        col_size(int) representing the number of cols in matrix
        data_elements(list of floats) representing the elements in matrix
    """
    def __init__(self,data = [[0,0],[0,0]]):
        
        matrix.__init__(self,data)
        
    
    def det(self):
        """Function to calculate the determinant of a square matrix
        
        Args:
            None
            
        Returns:
            float: determinant of the matrix    
        """
        return(self.data_elements[0][0] * self.data_elements[1][1] - self.data_elements[0][1] * self.data_elements[1][0])
    
    def __add__(self, other):
        
        """Function to add two square matrices
        
        Args:
            Other(matrix): matrix instance
            
        Returns:
            matrix: A sum matrix
        """
        result_a = matrix()
        result_a.data_elements[0][0] = self.data_elements[0][0] + other.data_elements[0][0]
        result_a.data_elements[0][1] = self.data_elements[0][1] + other.data_elements[0][1]
        result_a.data_elements[1][0] = self.data_elements[1][0] + other.data_elements[1][0]
        result_a.data_elements[1][1] = self.data_elements[1][1] + other.data_elements[1][1]
        
        return(result_a)
    
    def __sub__(self, other):
        
        """Function to subtract two square matrices
        
        Args:
            Other(matrix): matrix instance
            
        Returns:
            matrix: Result matrix after subtraction operation
        """
        result_s = matrix()
        result_s.data_elements[0][0] = self.data_elements[0][0] - other.data_elements[0][0]
        result_s.data_elements[0][1] = self.data_elements[0][1] - other.data_elements[0][1]
        result_s.data_elements[1][0] = self.data_elements[1][0] - other.data_elements[1][0]
        result_s.data_elements[1][1] = self.data_elements[1][1] - other.data_elements[1][1]
        
        return(result_s)
    
    def __repr__(self):
        """Function to output the characteristics of a matrix
        
        Args:
            None
            
        Returns:
            list: Characteristics of a matrix
        """
        return self.data_elements
         
        