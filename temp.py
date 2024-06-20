import subprocess as sp
import multiprocessing

def testing():
  sp.run(["ssh", "faster4.swtv", "python3 temp.py"])

jobs = []
for j in range(10):
  job = multiprocessing.Process(target=testing)
  jobs.append(job)
  job.start()

# for job in jobs:
#   job.join()

i = 0
for job in jobs:
  i += 1
  print(f"Job {i} is alive: {job.is_alive()}")
  job.terminate()
  job.join()
  print(f"Job {i} is alive: {job.is_alive()}")

import time
time.sleep(10)

# killall python3 in server
sp.run(["ssh", "faster4.swtv", "killall", "python3"])
