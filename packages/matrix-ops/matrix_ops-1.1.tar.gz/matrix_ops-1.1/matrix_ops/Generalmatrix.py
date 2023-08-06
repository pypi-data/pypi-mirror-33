class matrix:
    
    def __init__(self,data):
        """ General matrix class for instantiating matrices
        and performing operations
        
        Attributes:
            row_size(int) representing the number of rows in matrix
            col_size(int) representing the number of cols in matrix
            data_elements(list of floats) representing the elements in matrix
            """
        data_elements = data
        if (type(self.data_elements[0]) == list):
            row_size = len(self.data_elements)
            col_size = len(self.data_elements[0])
        else:
            row_size = 1
            col_size = len(self.data_elements)
        
    