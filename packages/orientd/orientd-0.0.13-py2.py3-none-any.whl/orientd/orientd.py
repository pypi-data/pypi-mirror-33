from flask import Flask, request
import Adafruit_PCA9685

app = Flask(__name__)

# Initialize the PCA9685
pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=3)

# Configure min & max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096
servo_mid = servo_min + int((servo_max - servo_min)/2)

# Define PI and slope
PI = 3.141592653589793
m = 450.0 / PI  # servo step size or slope


@app.route('/')
def index():
    return 'Orientd'


@app.route('/orientation', methods=['POST'])
def adjust():
    orientation = request.form['orientation']
    value = float(request.form['value'])
    result = 'Received %s update: %f' % (orientation, value)

    # Handle roll updates
    # Valid roll values are between 0 (looking straight down) and +PI (looking straight up)
    # PI/2 corresponds to looking straight forward and servo should be set to its midpoint.
    # Driving the servo positively from the midpoint corresponds to lower the cameras, driving
    # the servo negatively from the midpoint corresponds to raising the cameras.
    if orientation in ['roll']:

        if value >= 0:
            position = servo_mid - ((value - PI/2)*m)
            pwm.set_pwm(0, 0, int(position))
            log_result(orientation, value, int(position))

    # Handle yaw updates
    # Valid yaw values are between -PI/2 (looking to the right) and +PI/2 (looking to the left)
    # 0 corresponds to looking straight forward and servo should be set to its midpoint.
    # Driving the servo positively from the midpoint corresponds to turning the cameras right,
    # driving the servo negatively from the midpoint corresponds to turning the cameras left.
    if orientation in ['yaw']:

        # Only interested in radian values between -PI/2 and +PI/2
        if (value >= -PI/2) and (value <= PI/2):
            position = servo_mid + (value * m)
            pwm.set_pwm(1, 0, int(position))
            log_result(orientation, value, int(position))

    return result


def log_result(orientation, value, position):
    result = 'Received %s update: %.2f radians, setting servo position to %d' % (orientation, value, int(position))
    app.logger.debug(result)