import matplotlib.pyplot as plt
from numpy.core.fromnumeric import mean, sort
from numpy.core.numeric import zeros_like
from numpy.core.shape_base import vstack
from numpy.lib.function_base import median
from sklearn.linear_model import LinearRegression, Lasso, HuberRegressor, RANSACRegressor, TheilSenRegressor
import numpy as np
import json


#detector constants
NUM_LAYERS = 43
NUM_STAVES = 12 # per layer
NUM_CHIPS = 9 # per stave
NUM_PIXELS_WIDTH_CHIP = 1024
NUM_PIXELS_HEIGHT_CHIP = 512
MAX_WIDTH = NUM_PIXELS_WIDTH_CHIP*NUM_CHIPS
MAX_HEIGHT = NUM_PIXELS_HEIGHT_CHIP*NUM_STAVES

PIXEL_HEIGHT_AND_WIDTH= 0.02924


def find_IQR(l):
  #find the interquatile range of a dataset + Q1 and Q3

  sort(l)

  lower = l[:int(round(len(l)/2))]
  higher = l[int(round(len(l)/2)):]

  Q1 = lower[int(round(len(lower)/2))]
  Q3 = higher[int(round(len(higher)/2))]

  iqr = Q3 - Q1

  return Q1, Q3, iqr


def create_json_object_from_file(filename):

  with open(filename, "r") as file:
    root = json.load(file)

  return root

def apply_offsets_to_data(json_root, x, y):
  """
  x, y is full list off tracks not just one

  return new track with offsets applied
  """
  x_out = []
  y_out = []
  for x_track, y_track in zip(x, y):
    new_track_x = []
    new_track_y = []
    for i in range(len(x_track)):
      layer,stave,chip,x_,y_ = global_to_lscxy(x_track[i], y_track[i], i)

      x_offset = float(json_root["Layer "+str(layer)]["Stave "+str(stave)]["x"])
      y_offset = float(json_root["Layer "+str(layer)]["Stave "+str(stave)]["y"])

      new_track_x.append(x_track[i] + (x_offset/PIXEL_HEIGHT_AND_WIDTH))
      new_track_y.append(y_track[i] + (y_offset/PIXEL_HEIGHT_AND_WIDTH))

    x_out.append(new_track_x)
    y_out.append(new_track_y)

  return x_out, y_out
      
      

def conver_to_global_coordinates(layer, stave, chip, x, y):
  #convert a local hit to global coordinate

  ALPIDE_PIXELS_HEIGHT_NUM = 512    # 0 indexed
  ALPIDE_PIXELS_WIDTH_NUM = 1024 # 0 indexed
  
  x_out = 0
  y_out = 0
  chipID = chip
  if chipID >= 8:
    chipID -= 1;

  if stave % 2 == 0:
    x_out = (ALPIDE_PIXELS_WIDTH_NUM * chipID) + x
  else:
    x_out = (ALPIDE_PIXELS_WIDTH_NUM * chipID) + (ALPIDE_PIXELS_WIDTH_NUM - x)

  if layer % 2 != 0:
    total_pixel_width = ALPIDE_PIXELS_WIDTH_NUM*9
    x_out = total_pixel_width - x_out

  if stave % 2 == 0:
    y_out = (ALPIDE_PIXELS_HEIGHT_NUM * stave) + y
  else:
    y_out = (ALPIDE_PIXELS_HEIGHT_NUM * stave) + (ALPIDE_PIXELS_HEIGHT_NUM - y)

  return x_out,y_out,layer


def global_to_lscxy(x,y,z):
  """
  Global hit info to layer, stave, chip information
  
  This makes it easier to produces offsets that cross chip edges

  Returns layer, stave, chip, x, y
  """ 
  layer = 0
  stave = 0
  chip = 0
  x_ = 0
  y_ = 0
  
  layer = z
  stave = int(y/NUM_PIXELS_HEIGHT_CHIP) #round to floor value
  chip = int(x/NUM_PIXELS_WIDTH_CHIP) #round to floor value
  
  if stave == 12:
    stave -= 1

  if layer % 2 == 0:
    if chip > 6:
      chip += 1    
  else:
    if chip >= 2: #id 7 is never used
      chip = NUM_CHIPS - chip - 1
    else:
      chip = NUM_CHIPS - chip
  
  if layer % 2 == 0:
    if stave % 2 == 0:
      x_ = x % (NUM_PIXELS_WIDTH_CHIP)
    else:
      x_ = (NUM_PIXELS_WIDTH_CHIP - 1) - (x % (NUM_PIXELS_WIDTH_CHIP))
  else:
    total_pixels = (NUM_PIXELS_WIDTH_CHIP)*NUM_CHIPS - 1
    if stave % 2 == 0:
      x_ = (total_pixels - x) % (NUM_PIXELS_WIDTH_CHIP)
    else:
      x_ = (NUM_PIXELS_WIDTH_CHIP - 1) - ((total_pixels - x) % (NUM_PIXELS_WIDTH_CHIP))
  
  
  if stave % 2 == 0:
    y_ = y % NUM_PIXELS_HEIGHT_CHIP
  else:
    y_ = (NUM_PIXELS_HEIGHT_CHIP -1) - (y % NUM_PIXELS_HEIGHT_CHIP)
  

  if chip > 9: chip = 9
  assert chip != 7
  assert chip >= 0 and chip <= 9, "Expected >= 0 or <=9 was {} with x {}".format(chip, x)
  assert x_ < NUM_PIXELS_WIDTH_CHIP, "Expected <{}. Was {} layer {} stave {} chip {} x {} y {}".format(NUM_PIXELS_WIDTH_CHIP, x_, layer, stave,chip,x,y)
  assert y_ < NUM_PIXELS_HEIGHT_CHIP, "Expected <{}. Was {}".format(NUM_PIXELS_HEIGHT_CHIP, y_)
  assert stave >= 0 and stave < NUM_STAVES, "Was {} with y {}".format(stave, y)
  assert layer >= 0 and layer < NUM_LAYERS, "Was {}".format(layer)
  return layer, stave, chip, x_, y_


def plot_data(filename):
  x = []
  y = []
  z = []
  header = True
  with open(filename) as file:
    
    for line in file:
      if header:
        header = False
        continue 
      data = [int(x) for x in line.split(",")]
      
      x_ = 0 #global x
      y_ = 0 #global y
      z_ = 0 #global z

      layer = data[0]
      stave = data[1]
      chip = data[2]
      x_temp = data[3]
      y_temp = data[4]

      x_, y_, z_ = conver_to_global_coordinates(layer, stave, chip, x_temp, y_temp)
      x.append(x_)
      y.append(y_)
      z.append(z_)

  fig = plt.figure()
  ax = fig.add_subplot(projection='3d')

  ax.scatter(x[:100], z[:100], y[:100], s=0.5)
  ax.set_xlabel('X')
  ax.set_ylabel('Layer')
  ax.set_zlabel('Y')
  plt.show()

def plot_regression_line(filename, json_file, axis, n, corrected=True):
  x = []
  y = []
  z = []
  with open(filename) as file:
    pathX = []
    pathY = []
    pathZ = []
    header = True
    headers = {}
    curr_event = 0
    for line in file:
      if header:
        header = False

        for i, h in enumerate(line.split(",")):
            headers[h.rstrip("\n")] = i

        continue
      
      data = [int(x) for x in line.split(",")]
      if int(data[headers["eventID"]]) != curr_event:
        x.append(pathX.copy())
        y.append(pathY.copy())
        z.append(pathZ.copy())
        pathX.clear()
        pathY.clear()
        pathZ.clear()

        curr_event = int(data[headers["eventID"]])
        
      x_ = 0 #global x
      y_ = 0 #global y
      z_ = 0 #global z

      layer = data[0]
      stave = data[1]
      chip = data[2]
      x_temp = data[3]
      y_temp = data[4]

      x_, y_, z_ = conver_to_global_coordinates(layer, stave, chip, x_temp, y_temp)
      pathX.append(x_)
      pathY.append(y_)
      pathZ.append(z_)
    

  # first find the lest square regression line
  if corrected:
    x, y = apply_offsets_to_data(create_json_object_from_file(json_file), x, y)
  
  
  y_axis = z[:n]
  if axis == "y":
    x_axis = y[:n]
  else:
    x_axis = x[:n]
  
  for i in range(len(x_axis)):
    plt.scatter(x_axis[i], y_axis[i])

  # xaxis = np.asarray([np.ones(len(x_axis)), x_axis]).T
  # beta_0, beta_1 = np.linalg.inv(xaxis.T @ xaxis) @ xaxis.T @ y_axis

  # x_lin_space = np.linspace(min(x_axis), max(x_axis))
  # y_hat = beta_0 + beta_1 * x_lin_space

  
  #plt.plot(x_lin_space, y_hat, color='r', label='LinearRegression')

  plt.xlabel("Hit on {} axis".format(axis))
  plt.ylabel("Layer")
  plt.xlim([-5000,15000])
  plt.show()


x_b = plot_regression_line("simData.csv", "testoutputfile.json", "x", 100, False)
y_b = plot_regression_line("simData.csv", "testoutputfile.json", "y", 100, False)
x_b = plot_regression_line("simData.csv", "testoutputfile.json", "x", 100, True)
y_b = plot_regression_line("simData.csv", "testoutputfile.json", "y", 100, True)

# plot_data("simData.csv")





# x = x_b[1][0]
# z = x_b[2][0]
# y = x_b[3][0]

# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')

# ax.scatter(x, y, z)
# x = [x_b[0] for i in range(43)]
# z = [y_b[0] for i in range(43)]
# y = [i for i in range(43)]
# ax.plot(x, y, z, color='r')
# ax.set_xlabel('X')
# ax.set_ylabel('Layer')
# ax.set_zlabel('Y')
# ax.set_xlim(0,1024)
# ax.set_ylim(0,43)
# ax.set_zlim(0,512)
# plt.show()