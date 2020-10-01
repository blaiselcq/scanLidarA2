from threading import Thread
from rplidar import RPLidar
import time
from math import pi

class Lidar(Thread):
    
    def __init__(self,port,baud,data,limit = 1000):
        Thread.__init__(self)
        self.lidar = RPLidar(port = port, baudrate = baud)
        try:
            print(self.lidar.get_info())
        except Exception as e:
            print(e)
            self.lidar.eteindre()
            self.lidar.reset()
            self.lidar.connect()
            self.lidar.start_motor()
            
        self.data = data
        self.limit = limit
    
    def run(self):
        time.sleep(1)
        for measurment in self.lidar.iter_measurments(max_buf_meas=self.limit):
            s = len(self.data[0])
            if s >= self.limit:
                self.data[0].pop(0)
                self.data[1].pop(0)
            self.data[0].append(measurment[2]*pi/180) #agle en rad
            self.data[1].append(measurment[3]/1000) #distance en m

    def join(self, timeout=None):
        self.eteindre()
        Thread.join(self, timeout)

    def eteindre(self):
        self.lidar.stop_motor()
        self.lidar.stop()
        self.lidar.disconnect()

if __name__ == "__main__":

    angle = []
    dist = []
    data = (angle,dist)


    lidar = Lidar("COM13",115200,data)
    lidar.start()
    time.sleep(10)
    lidar.join()