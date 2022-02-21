#always start at chip id 0, layer arrangement not considered
#x,y offset value for each chip
import random

with open("dummy_alignment_output_file.txt", "w") as file:
  for layer in range(43):
    for stave in range(12):
      for chip in range(10):
        if chip == 7:
          continue
        x = int(random.random()*11)
        y = int(random.random()*11)
        file.write("{},{}\n".format(str(x).zfill(2),str(y).zfill(2)))

