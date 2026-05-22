import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class KararMerkezi3D(Node):
    def __init__(self):
        super().__init__('karar_merkezi_3d')
        self.motor_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        self.get_logger().info('3D Otonom Sürüş Başladı! Lazer filtre devrede...')
        self.donus_sayaci = 0

    def scan_callback(self, msg):
        # LiDAR'in 360 derecelik verisinden sadece TAM ÖNÜ (165-195 derece arasini) al.
        on_lazerler = msg.ranges[165:195]
        
        # Filtreleme: Sensörün sonsuz (inf) veya çok düşük (kendi gövdesi) hatalarını ayıkla
        gecerli_okumalar = [mesafe for mesafe in on_lazerler if 0.35 < mesafe < 10.0 and not math.isinf(mesafe)]
        
        if not gecerli_okumalar:
            en_yakin_mesafe = 10.0 # Önümüz tamamen boşsa maksimum uzaklık varsay
        else:
            en_yakin_mesafe = min(gecerli_okumalar)

        hareket = Twist()

        if self.donus_sayaci > 0:
            self.donus_sayaci -= 1
            hareket.linear.x = 0.0
            hareket.angular.z = 1.5
            
        elif en_yakin_mesafe < 0.8: # Güvenlik mesafesini 0.8 metreye çektik
            self.get_logger().info(f'Engel Algilandi! (Mesafe: {en_yakin_mesafe:.2f}m) Manevra baslatiliyor.')
            self.donus_sayaci = 15
            hareket.linear.x = 0.0
            hareket.angular.z = 1.5
            
        else:
            hareket.linear.x = 0.8
            hareket.angular.z = 0.0

        self.motor_pub.publish(hareket)

def main(args=None):
    rclpy.init(args=args)
    node = KararMerkezi3D()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
