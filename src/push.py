# Merge/Push functions for 2048 game
# Thomas Kabalin
# 10/04/2024

# NOTE: This is currently hardcoded to only work with grids of size 4

# This could be coded much more efficiencly, but was originally done 
# to meet the requirements of an intro to programming assignment

def push_up (grid):
    """merge grid values upwards"""
    # Loop through the columns
    for c in range(4):
        merge = []
        
        # Loop through the rows, adding each non-zero value to a new array called merge and setting the grid values to 0
        for r in range(4):
            value = grid[r][c]
            if value != 0:
                merge.append(grid[r][c])
                grid[r][c] = 0
        
        index = 0  
        # Loop until there has been an attempt to merge all values in the merge array
        while index < len(merge)-1:
            # Check if adjacent values are equal
            if merge[index] == merge[index+1]:  
                # If they are, double the first and delete the second
                merge[index] *= 2
                del merge[index+1]
                index += 1
            else:
                # Move to the next value
                index += 1
        
        # Add the merged values back into the grid
        for r in range(len(merge)):
            grid[r][c] = merge[r]
                
    return grid    
    
def push_down(grid):
    """merge grid values downwards"""
    # Loop through the columns
    for c in range(4):
        merge = []
        
        # Loop through the rows in reverse order, adding each non-zero value to a new array called merge and setting the grid values to 0
        for r in range(3, -1, -1):
            value = grid[r][c]
            if value != 0:
                merge.append(grid[r][c])
                grid[r][c] = 0
        
                
        index = 0
        # Loop until there has been an attempt to merge all values in the merge array        
        while index < len(merge) - 1:
            # Check if adjacent values are equal            
            if merge[index] == merge[index + 1]:
                # If they are, double the first and delete the second                
                merge[index] *= 2
                del merge[index + 1]
                index += 1
            else:
                # Move to the next value
                index += 1

        # Update the grid with the merged values
        for r in range(len(merge)):
            grid[3 - r][c] = merge[r]  # Reverse the index when updating due to reversed grid

    # Reverse the order of rows in the grid back to the original
        
    return grid

def push_left(grid):
    """merge grid values to the left"""
    # Loop through the rows
    for r in range(4):
        merge = []
        
        # Loop through the columns, adding each non-zero value to a new array called merge and setting the grid values to 0
        for c in range(4):
            value = grid[r][c]
            if value != 0:
                merge.append(grid[r][c])
                grid[r][c] = 0
        
        index = 0
        # Loop until there has been an attempt to merge all values in the merge array        
        while index < len(merge) - 1:
            # Check if adjacent values are equal            
            if merge[index] == merge[index + 1]:
                # If they are, double the first and delete the second                
                merge[index] *= 2
                del merge[index + 1]
                index += 1
            else:
                # Move to the next value
                index += 1

        # Update the grid with the merged values
        for c in range(len(merge)):
            grid[r][c] = merge[c]
    
    return grid

def push_right(grid):
    """merge grid values to the right"""
    # Loop through the rows
    for r in range(4):
        merge = []
        
        # Loop through the columns in reverse order, adding each non-zero value to a new array called merge and setting the grid values to 0
        for c in range(3, -1, -1):
            value = grid[r][c]
            if value != 0:
                merge.append(grid[r][c])
                grid[r][c] = 0
         
        index = 0
        # Loop until there has been an attempt to merge all values in the merge array        
        while index < len(merge) - 1:
            # Check if adjacent values are equal            
            if merge[index] == merge[index + 1]:
                # If they are, double the first and delete the second                
                merge[index] *= 2
                del merge[index + 1]
                index += 1
            else:
                # Move to the next value
                index += 1

        # Update the grid with the merged values (in reverse order)
        for c in range(len(merge)):
            grid[r][3 - c] = merge[c] 
    
    return grid
