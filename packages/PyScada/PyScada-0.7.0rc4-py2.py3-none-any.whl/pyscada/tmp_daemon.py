## LOOPs
'''
    (1  ,  '1 Second'),
    (2,    '2 Seconds'),
    (5  ,  '5 Seconds'),
    (10 ,  '10 Seconds'),
    (15 ,  '15 Seconds'),
    (30 ,  '30 Seconds'),
    (60 ,  '1 Minute'),
    (150,  '2.5 Mintues'),
    (300,  '5 Minutes'),
    (360,  '6 Minutes (10 times per Hour)'),
    (600,  '10 Minutes'),
    (900,  '15 Minutes'),
    (1800, '30 Minutes'),
    (3600, '1 Hour'),
'''
import time
dt_min = 5
tasklist = ((2,'task 1 (2 s)',),
            (5,'task 2 (5 s)',),
            (2,'task 3 (2 s)',),
            (1,'task 4 (1 s)',),
            (10,'task 5 (10 s)',),)

for item in tasklist:
    dt_min = min(dt_min,item[0])
i = dt_min
while i < 100:
    dt_start = time.time()
    for item in tasklist:
        if i%item[0]==0:
            print '%s run %s'%(str(i),item[1])
    
    i += dt_min
    time.sleep(max(0,dt_min-time.time()-dt_start))