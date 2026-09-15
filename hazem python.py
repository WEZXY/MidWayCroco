import rclpy
from rclpy.node import Node
from custom_msg_interfaces.msg import ArduinoReading, ArduinoActions

class SmartHomeBrain(Node):
    def __init__(self):
        super().__init__('smart_home_brain')
        self.get_logger().info("Smart Home Brain Started (Direct Values Mode)")

        self.sub = self.create_subscription(
            ArduinoReading,
            'arduino_reading',
            self.reading_callback,
            10
        )
        self.pub = self.create_publisher(
            ArduinoActions,
            'arduino_writing',
            10
        )

        self.light = 0
        self.current_state = None  
        self.LIGHT_HIGH = 700
        self.LIGHT_LOW = 400

        self.create_timer(0.1, self.timer_callback)

    def reading_callback(self, msg):
        self.light = msg.light

    def timer_callback(self):
        new_state = None

        if self.light > self.LIGHT_HIGH:
            new_state = "DAY"
        elif self.light < self.LIGHT_LOW:
            new_state = "NIGHT"

        if new_state is not None and new_state != self.current_state:
            self.current_state = new_state  
            
            if new_state == "DAY":
                self.get_logger().info('It is DAY: Servo -> 180, LED -> 0')
                self.send_command("SERVO:180")
                self.send_command("LED:0")
                
            elif new_state == "NIGHT":
                self.get_logger().info('It is NIGHT: Servo -> 0, LED -> 1')
                self.send_command("SERVO:0")
                self.send_command("LED:1")

    def send_command(self, cmd):
        msg = ArduinoActions()
        msg.command = cmd
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SmartHomeBrain()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()