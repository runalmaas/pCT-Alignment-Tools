import matplotlib.pyplot as plt
import sys


################################################################################################
#       This script is not friendly for large data. Try to keep it below 100.000 points        #
################################################################################################


def plot_coordinates(filename, filter_proton, num_points):
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
    counter = num_points
    for line in file:
      if (counter <= 0): break
      
      #if header line create dictionary and skip
      if header_line:
        header_line = False

        for i,h in enumerate(line.split(",")):
          headers[h] = i

        continue

      values = line.split(",")

      if filter_proton:
        if(int(values[headers["PDGEncoding"]]) != 2212): continue

      x.append(float(values[headers["posX"]]))
      y.append(float(values[headers["posY"]]))
      z.append(float(values[headers["posZ"]]))
      
      counter -= 1


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
  if str(sys.argv[2]) == "True" or str(sys.argv[2]) == "1":
    plot_coordinates(str(sys.argv[1]), True, int(sys.argv[3]))
  else:
    plot_coordinates(str(sys.argv[1]), False, int(sys.argv[3]))
else:
  print("Please provide a filename.")