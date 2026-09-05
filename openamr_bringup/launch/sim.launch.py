import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    os.environ['GZ_SIM_RENDER_ENGINE']='ogre'
    os.environ['GZ_SIM_RENDER_ENGINE_GUI']='ogre'
    # Get package paths
    pkg_openamr_description = get_package_share_directory('openamr_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    # Define URDF path
    urdf_file = os.path.join(pkg_openamr_description, 'urdf', 'openamr.urdf.xacro')
    
    # 1. Robot State Publisher Node (Now using sim time)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', urdf_file]), 'use_sim_time': True}]
    )
    
    # 2. Gazebo Simulator (Loading the custom world WITH the sensor plugin)
    pkg_openamr_bringup = get_package_share_directory('openamr_bringup')
    world_file = os.path.join(pkg_openamr_bringup, 'worlds', 'safe_sensors.sdf')
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r -v 4 {world_file}'}.items()
    )
    
    # 3. Spawn Robot Entity in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'openamr', '-z', '0.2'],
        output='screen'
    )
    
    # 4. Gazebo to ROS 2 Clock Bridge
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock','/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'],
        output='screen'
    )

    # 5. Spawners for the controllers
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_entity,
        clock_bridge,
        diff_drive_spawner,
        joint_broad_spawner
    ])
