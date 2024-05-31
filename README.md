# 007 Running Step Rate
Measure and train step rate while running, range from 30~300 steps/min.

### Nodes Required: 3 
- Sensing (1): 
  - Shank: lateral side with switch pointing up
- Feedback (2): 
  - Max: Node used to provide haptic feedback when the participant is above the maximum step rate threshold set in the app configuration panel.
  - Min: Node used to provide haptic feedback when the participant is below the minimum step rate threshold set in the app configuration panel.

## Algorithm & Calibration
### Algorithm Information
This app uses the autocorrelation function (ACF) to estimate the step rate based on the IMU sensor data. It calculates the offset of data with the maximum correlation to get the most likely period of data.

This algorithm is inspired by:
[1]Pan, Meng-Shiuan, and Hsueh-Wei Lin. "A step counting algorithm for smartphone users:
   Design and implementation." IEEE Sensors Journal 15.4 (2014): 2296-2305.

### Calibration Process:
The magnitude of the three axis gyroscope is used, so alignment of the node is not important. It is important that the node is placed tightly on the segment to reduce soft tissue artifacts and segment-node relative movement. No calibration is needed.

## Description of Data in Downloaded File
- time (sec): time since trial start
- StepRate (step/min): current step during running (based on the sliding window)
- stepRate_low: The lower threshold set by the user in the App configuration Panel.
- stepRate_high: The upper threshold set by the user in the App configuration Panel.
- low_feedback_state: feedback status for if the sensor has crossed the min step rate threshold. 
  - 0 is “feedback off”
  - 1 is “feedback on” 
- high_feedback_state: feedback status for if the sensor has crossed the max step rate threshold. 
  - 0 is “feedback off”
  - 1 is “feedback on” 
- SensorIndex: index of raw sensor data
- AccelX/Y/Z (m/s^2): raw acceleration data
- GyroX/Y/Z (deg/s): raw gyroscope data
- MagX/Y/Z (μT): raw magnetometer data
- Quat1/2/3/4: quaternion data (Scaler first order)
- Sampletime: timestamp of the sensor value
- Package: package number of the sensor value
