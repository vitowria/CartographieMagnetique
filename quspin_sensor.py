import serial
import binascii
import threading
import time

class QUSPIN:
    """
    A class used to retrieve Quspin sensor information in Python
    ...

    Attributes
    ----------
    port : int
        The COM port in which the sensor is connected
    serial_comm : PySerial object
        The attribute where the open serial port is stored
    last_message : string
        Where the last message received from the sensor is stored, regardless of type
    cell_temp_error : int
        Error in temperature on the sensor (digital measure)
    cell_temp_control_voltage : int
        Temperature control voltage (digital measure)
    laser_on : bool
        Indicates state of the sensor laser
    cell_temperature_lock : bool
        Indicates if the temperature is locked
    laser_lock : bool
        Indicates if the laser state is locked
    field_zeroing : bool
        Indicates if field zeroing is activated
    master_mode : bool
        Indicates if sensor is in master mode or slave mode
    magnetometer_out : float
        Indicates the last measure of the magnetometer (in pT)
    stopFlag : bool
        Stops the thread in which the measures are taken
    queue_length : int
        Length of list of measures
    queue : list
        List of last queue_length measures, defined during initialization
    
    Methods
    -------
    start()
        Starts the parallel thread that reads the measures and updates the variable
    stop()
        Stops the thread and closes the serial port
    auto_start_procedure()
        Runs the Quspin auto start routine
    show_status()
        Switchs the sensor into status output mode
    show_measure()
        Switchs the sensor into measure output mode
    field_zero(val : bool)
        Activates or deactivates field zeroing
    calibrate()
        Runs calibration routine
    z_axis()
        Measures the magnetic field according to the z axis
    y_axis()
        Measures the magnetic field according to the y axis
    reboot()
        Reboots the sensor's internal microcontroller
    __read()
        Function to read the output from the serial port. Private method
    """

    port = None
    serial_comm = None
    last_message = None

    cell_temp_error = None
    cell_temp_control_voltage = None

    laser_on = False
    cell_temperature_lock = False
    laser_lock = False
    field_zeroing = False
    master_mode = False

    magnetometer_out = None

    stopFlag = False

    queue = []
    queue_length = 100

    def __init__(
        self,
        port : str='COM8',
        queue_length : int=100
    ) -> None:
        self.port = port
        self.serial_comm = serial.Serial(port, 115200, timeout=0)
        self.last_message = ''
        self.cell_temp_error = None
        self.cell_temp_control_voltage = None
        self.laser_on = False
        self.cell_temperature_lock = False
        self.laser_lock = False
        self.field_zeroing = False
        self.master_mode = False
        self.magnetometer_out = None
        self.stopFlag = False
        self.queue_length = queue_length
        self.queue = []
    
    def __del__(
        self
    ) -> None:
        self.stop()
    
    def start(
        self
    ) -> None:
        self.thread = threading.Thread(target=self.__read)
        self.thread.start()

    def stop(
        self
    ) -> None:
        self.stopFlag = True
        self.serial_comm.close()
    
    def auto_start_procedure(
        self
    ) -> None:
        self.serial_comm.write(b'>')
    
    def show_status(
        self
    ) -> None:
        self.serial_comm.write(b'8')

    def show_measure(
        self
    ) -> None:
        self.serial_comm.write(b'7')
    
    def field_zero(
        self,
        val : bool
    ) -> None:
        if val:
            self.serial_comm.write(b'D')
        else:
            self.serial_comm.write(b'E')

    def calibrate(
        self
    ) -> None:
        self.serial_comm.write(b'9')
    
    def z_axis(
        self
    ) -> None:
        self.serial_comm.write(b'C')

    def y_axis(
        self
    ) -> None:
        self.serial_comm.write(b'F')

    def reboot(
        self
    ) -> None:
        self.serial_comm.write(b'e')

    def __process_message(
        self,
        msg : str
    ) -> str:
        #print(msg)
        if msg[0]=='~':
            if msg[1:3]=='04':
                self.cell_temp_error = int(msg[3:])
            if msg[1:3]=='05':
                self.cell_temp_control_voltage = int(msg[3:])
        elif msg[0]=='|':
            if msg[1]=='1':
                if msg[2]=='1':
                    self.laser_on=True
                else:
                    self.laser_on=False
            if msg[1]=='2':
                if msg[2]=='1':
                    self.cell_temperature_lock=True
                else:
                    self.cell_temperature_lock=False
            if msg[1]=='3':
                if msg[2]=='1':
                    self.laser_lock=True
                else:
                    self.laser_lock=False
            if msg[1]=='4':
                if msg[2]=='1':
                    self.field_zeroing=True
                else:
                    self.field_zeroing=False
            if msg[1]=='5':
                if msg[2]=='1':
                    self.master_mode=True
                else:
                    self.master_mode=False
        elif msg[0]=='!':
            self.magnetometer_out = (int(msg[1:])-8388608)*0.01
            if len(self.queue)<self.queue_length:
                self.queue.append(self.magnetometer_out)
            else:
                self.queue.pop(0)
                self.queue.append(self.magnetometer_out)
        else:
            print(msg)
    
    def __repr__(
        self
    ) -> str:
        return f'''QUSPIN
Temp error: {self.cell_temp_error}
Temp voltage: {self.cell_temp_control_voltage}
Laser on: {self.laser_on}
Cell temperature lock: {self.cell_temperature_lock}
Laser lock: {self.laser_lock}
Field zeroing: {self.field_zeroing}
Master mode: {self.master_mode}

Last mesure: {self.magnetometer_out}
        '''

    def __read(
        self
    ) -> str:
        total = ""
        while self.stopFlag==False:
            try:
                readBytes = self.serial_comm.read()
                msg = binascii.hexlify(readBytes)
                msg = msg.decode('utf-8')
                bytes_object = bytes.fromhex(msg)
                ascii_string = bytes_object.decode("ASCII")
                if '\n' in ascii_string:
                    total.replace('\r','')
                    self.last_message = total
                    self.__process_message(self.last_message)
                    total=''
                else:
                    total += ascii_string
            except:
                pass
        return total

if __name__=='__main__':
    q = QUSPIN('COM8')
    q.z_axis()
    q.auto_start_procedure()
    q.start()
    q.show_measure()
    while True:
        print(q.magnetometer_out)
        time.sleep(0.1)