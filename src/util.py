# Functions to manipulate 2D arrays
# Thomas Kabalin
# 10/04/2024

# NOTE: This is currently hardcoded to only work with grids of size 4
# Some of the functions are unnecessary in the 2048-desktop game

def create_grid(grid):
  """create a 4x4 array of zeroes within grid"""
  # Loop through the rows, adding four columns with 0s
  for row in range(4):
      grid.append([0] * 4)  

  return grid

def print_grid (grid): 
  """print out a 4x4 grid in 5-width columns within a box"""
  print('+--------------------+')
  
  # Loop through the rows
  for row in range(4):
    print('|',end='')
    
    # Loop through the columns
    for col in range(4):
      # Check if the current value is zero. If it is not, print the value left alliged with a fixed width of 5
      if grid[row][col] != 0:
        print('{0:<5}'.format(grid[row][col]),end='')
      else:
        print('{0:<5}'.format(''),end='')
    print('|')
  
  print('+--------------------+')

def check_lost (grid):
  """return True if there are no 0 values and there are no adjacent values that are equal; otherwise False"""
  for row in range(4):
    for col in range(4): 
      # Return false if a zero is found
      if grid[row][col] == 0:
        return False
      
      # Get the current number from the grid
      current_number = grid[row][col]
      # Perform checks of adjacent numbers, ensuring not to exceed the bounds of the list      
      # Check above
      if row > 0 and grid[row - 1][col] == current_number:
          return False
      # Check below
      if row < 3 and grid[row + 1][col] == current_number:
          return False
      # Check left
      if col > 0 and grid[row][col - 1] == current_number:
          return False
      # Check right
      if col < 3 and grid[row][col + 1] == current_number:
          return False
        
  return True

def check_won (grid): 
  """return True if a value>=2048 is found in the grid; otherwise False"""
  # Loop through the rows and columns looking for a value >= 2048
  for row in range(4):
    for col in range(4):
      if grid[row][col] >= 2048:
        return True
  
  return False
  
def copy_grid (grid):
  """return a copy of the given grid"""
  # Create a new, blank 4x4 grid
  new_grid = [[0]*4,[0]*4,[0]*4,[0]*4]
  for row in range(4):
    for col in range(4):
      # Add the value from the old grid to the new grid
      new_grid[row][col] = grid[row][col]
  
  return new_grid

def grid_equal (grid1, grid2): 
  """check if 2 grids are equal - return boolean value"""
  # Compare the 2 grids to see if they are equal
  if grid1 == grid2:
    return True
  else:
    return False