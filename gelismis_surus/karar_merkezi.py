import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import random

class KararMerkezi(Node):
    """
    Otonom Alan Tarama ve Engelden Kaçma (Robot Süpürge) Algoritması
    ROS 2 Jazzy LTS üzerinde geliştirilmiştir.
    """
    def __init__(self):
        super().__init__('karar_merkezi')
        self.motor_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        
        self.gercek_x = 5.5
        self.gercek_y = 5.5
        
        self.donus_sayaci = 0
        self.uzaklasma_sayaci = 0
        self.aktif_donus_hizi = 0.0
        
        # Karar alma frekansı artırıldı (Saniyede 20 okuma)
        self.create_timer(0.05, self.beyin_dongusu)
        self.get_logger().info('Otonom sürüş sistemi aktif. Alan taranıyor...')

    def pose_callback(self, msg):
        self.gercek_x = msg.x
        self.gercek_y = msg.y

    def beyin_dongusu(self):
        dx = min(self.gercek_x, 11.0 - self.gercek_x)
        dy = min(self.gercek_y, 11.0 - self.gercek_y)
        mesafe = min(dx, dy)

        msg = Twist()

        if self.donus_sayaci > 0:
            self.donus_sayaci -= 1
            msg.linear.x = 0.0
            msg.angular.z = self.aktif_donus_hizi
            
            if self.donus_sayaci == 0:
                self.uzaklasma_sayaci = 15  # Manevra sonrası kaçış ivmesi
                
        elif self.uzaklasma_sayaci > 0:
            self.uzaklasma_sayaci -= 1
            msg.linear.x = 3.0
            msg.angular.z = 0.0
            
        elif mesafe < 0.8:
            # Güvenlik sınırı 0.8 metreye çıkarıldı, duvar temasları (clamping) önlendi
            self.get_logger().info(f'Engel algılandı! (Mesafe: {mesafe:.2f}m) Yön hesaplanıyor...')
            self.donus_sayaci = random.randint(15, 30)
            self.aktif_donus_hizi = random.uniform(1.8, 3.5)
            
            if random.choice([True, False]):
                self.aktif_donus_hizi *= -1.0
                
            msg.linear.x = 0.0
            msg.angular.z = self.aktif_donus_hizi
            
        else:
            msg.linear.x = 3.0
            msg.angular.z = 0.0

        self.motor_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = KararMerkezi()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
