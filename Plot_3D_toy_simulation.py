import matplotlib.pyplot as plt
import sys


################################################################################################
#       This script is not friendly for large data. Try to keep it below 100.000 points        #
################################################################################################

#detector constants
NUM_LAYERS = 43
NUM_STAVES = 12 # per layer
NUM_CHIPS = 9 # per stave
NUM_PIXELS_WIDTH_CHIP = 1023
NUM_PIXELS_HEIGHT_CHIP = 511
MAX_WIDTH = NUM_PIXELS_WIDTH_CHIP*NUM_CHIPS
MAX_HEIGHT = NUM_PIXELS_HEIGHT_CHIP*NUM_STAVES

PIXEL_HEIGHT_AND_WIDTH= 0.02924


def conver_to_global_coordinates(layer, stave, chip, x, y):
  #convert a local hit to global coordinate
  
  x_out = 0
  y_out = 0
  chipID = chip
  if chipID >= 8:
    chipID -= 1;

  if stave % 2 == 0:
    x_out = (NUM_PIXELS_WIDTH_CHIP * chipID) + x
  else:
    x_out = (NUM_PIXELS_WIDTH_CHIP * chipID) + (NUM_PIXELS_WIDTH_CHIP - x)

  if layer % 2 != 0:
    total_pixel_width = NUM_PIXELS_WIDTH_CHIP*9
    x_out = total_pixel_width - x_out

  if stave % 2 == 0:
    y_out = (NUM_PIXELS_HEIGHT_CHIP * stave) + y
  else:
    y_out = (NUM_PIXELS_HEIGHT_CHIP * stave) + (NUM_PIXELS_HEIGHT_CHIP - y)
  return x_out,y_out,layer



def plot_coordinates(filename):
    """
    Plot every x,y,z coordinate in the given file
    This file should be a .csv file containing the headers: posX, posY, and posZ
    Representing the coordinates for x,y, and z for every hit

    Read each value into a list x,y, or z and plot these lists into a 3D plot 
    """

    with open(filename, "r") as file:

        x = []
        y = []
        z = []

        headers = {}

        header_line = True
        for line in file:

            # if header line create dictionary and skip
            if header_line:
                header_line = False

                for i, h in enumerate(line.split(",")):
                    headers[h] = i

                continue

            values = line.split(",")

            layer = int(values[headers["Layer"]])
            stave = int(values[headers["Stave"]])
            chip = int(values[headers["Chip"]])
            x_ = int(values[headers["X"]])
            y_ = int(values[headers["Y"]])
            
            global_coord = conver_to_global_coordinates(layer, stave, chip, x_, y_)

            x.append(global_coord[0])
            y.append(global_coord[1])
            z.append(global_coord[2])
            

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.scatter(x, z, y, s=0.5)
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_zlabel('Y')
    plt.show()


#  Take first argument as parameter for ploting function,
#  Second argument defines if only proton hits should be plotted: True/* or 1/* (* = wildcard)
#  else print error message.
if len(sys.argv) > 1:
  plot_coordinates(str(sys.argv[1]))

