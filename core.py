import logging
import numpy as np
from sage.base_app import BaseApp

if __name__ == "__main__":
    from steprate import StepRate
else:
    from .steprate import StepRate



class Core(BaseApp):

    ###########################################################
    # INITIALIZE APP
    ###########################################################
    def __init__(self, my_sage):
        BaseApp.__init__(self, my_sage, __file__)

        # Set up the app
        self.iteration = 0
        self.steprate = 0.0
        self.fnc_button = 0
        self.GyroMotionCnt = 0     
        self.my_stepRate = StepRate(
            datarate=self.info["datarate"],
            max_steprate=self.info["max_steprate"],
            min_steprate=self.info["min_steprate"],
        )

        self.stepRate_high = self.config["stepRate_high"]
        self.stepRate_low = self.config["stepRate_low"]

        self.NodeNum_shank = self.info["sensors"].index("Shank")
        self.NodeNum_feedback_min = self.info["feedback"].index("Min")
        self.NodeNum_feedback_max = self.info["feedback"].index("Max")
        self.user_defined_status = ""

        self.datawindow = []
        self.high_feedback_state = 0
        self.low_feedback_state = 0

    ###########################################################
    # CHECK NODE CONNECTIONS
    ###########################################################
    def check_status(self):
        # check if the requirement if satisfied
        sensors_count = self.get_sensors_count()
        feedback_count = self.get_feedback_count()
        logging.debug("config pulse length {}".format(self.info["pulse_length"]))
        err_msg = ""
        if sensors_count < len(self.info["sensors"]):
            err_msg += "App requires {} sensors but only {} are connected".format(
                len(self.info["sensors"]), sensors_count
            )
        if self.config["feedback_enabled"] and feedback_count < len(
            self.info["feedback"]
        ):
            err_msg += "App require {} feedback but only {} are connected".format(
                len(self.info["feedback"]), feedback_count
            )
        if err_msg != "":
            return False, err_msg
        return True, "Now running Step Rate app"

    #############################################################
    # UPON STARTING THE APP
    # If you have anything that needs to happen before the app starts
    # collecting data, you can uncomment the following lines
    # and add the code in there. This function will be called before the
    # run_in_loop() function below.
    #############################################################
    # def on_start_event(self):
    #     print("In On Start Event")

    ###########################################################
    # RUN APP IN LOOP
    ###########################################################
    def run_in_loop(self):
        # Get next data packet
        data = self.my_sage.get_next_data()
        gyroX = data[self.NodeNum_shank]["GyroX"]
        gyroY = data[self.NodeNum_shank]["GyroY"]
        gyroZ = data[self.NodeNum_shank]["GyroZ"]
        gyro_mag = np.sqrt(np.square(gyroX) + np.square(gyroY) + np.square(gyroZ))
        self.datawindow.append(gyro_mag)
        self.iteration = self.iteration + 1
        # These threshold are empirical values, make sure the sensor goes into movement state.
        if (gyro_mag > 100) and (self.GyroMotionCnt < 180):
            self.GyroMotionCnt = self.GyroMotionCnt + 4
        elif self.GyroMotionCnt > 0:
            self.GyroMotionCnt = self.GyroMotionCnt - 1
        if self.iteration % 100 == 0:
            print("Movement Cnt")
            print(self.GyroMotionCnt)

        if (
            self.iteration % int(self.info["windowLength"] * self.info["datarate"])
        ) == 0:
            if self.GyroMotionCnt > 80:  # enable
                self.steprate = self.my_stepRate.cal_steprate(self.datawindow)
                
                if (self.steprate > 240):  # if the step rate is over detection range, force to an invalid value.                    
                    self.steprate = 20  # invalid value
                elif self.steprate < 120:                    
                    self.steprate = 10  # invalid value
            else:
                self.steprate = 0

            self.user_defined_status = f"Current Step Rate is: {self.steprate} per minute"

            self.datawindow = []
            if self.config["feedback_enabled"]:
                self.high_feedback_state = int(self.steprate > self.stepRate_high)
                self.low_feedback_state = int(self.steprate < self.stepRate_low)
            else:
                self.high_feedback_state = 0
                self.low_feedback_state = 0

            # Turn on/off feedback based on the state.
            self.toggle_feedback(
                self.NodeNum_feedback_min,
                self.info["pulse_length"],
                self.low_feedback_state,
            )
            self.toggle_feedback(
                self.NodeNum_feedback_max,
                self.info["pulse_length"],
                self.high_feedback_state,
            )

        my_data = {
            "time": [self.iteration / self.info["datarate"]],
            "stepRate": [int(self.steprate)],
            "stepRate_low": [self.stepRate_low],
            "stepRate_high": [self.stepRate_high],            
            "low_feedback_state": [self.low_feedback_state],
            "high_feedback_state": [self.high_feedback_state],
            "user_defined_status": [self.user_defined_status],
        }

        self.my_sage.save_data(data, my_data)
        self.my_sage.send_stream_data(data, my_data)
        return True

    #############################################################
    # UPON STOPPING THE APP
    # If you have anything that needs to happen after the app stops,
    # you can uncomment the following lines and add the code in there.
    # This function will be called after the data file is saved and
    # can be read back in for reporting purposes if needed.
    #############################################################
    # def on_stop_event(self, stop_time):
    #     print(f"In On Stop Event: {stop_time}")

    def toggle_feedback(self, feedbackNode=0, duration=1, feedback_state=0):
        if feedback_state==1:
            self.my_sage.feedback_on(feedbackNode, duration)
        else:
            self.my_sage.feedback_off(feedbackNode)