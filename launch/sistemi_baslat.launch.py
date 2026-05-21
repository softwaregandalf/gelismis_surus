from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='turtlesim', executable='turtlesim_node', name='simulasyon'),
        Node(package='gelismis_surus', executable='karar_merkezi', name='sofor_sistemi', output='screen')
    ])
