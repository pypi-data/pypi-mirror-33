class matrix:
    
    def __init__(self,data):
        """ General matrix class for instantiating matrices
        and performing operations
        
        Attributes:
            row_size(int) representing the number of rows in matrix
            col_size(int) representing the number of cols in matrix
            data_elements(list of floats) representing the elements in matrix
            """
        self.data_elements = data
        if (type(self.data_elements[0]) == list):
            self.row_size = len(self.data_elements)
            self.col_size = len(self.data_elements[0])
        else:
            self.row_size = 1
            self.col_size = len(self.data_elements)
        
    