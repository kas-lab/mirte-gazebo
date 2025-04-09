# Copyright 2025 Gustavo Rezende Silva
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import LaunchConfigurationEquals
from launch.conditions import LaunchConfigurationNotEquals
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
  # Use simulation time
  use_sim_time = LaunchConfiguration("use_sim_time", default='true')
  headless = LaunchConfiguration('headless')

  headless_arg = DeclareLaunchArgument(
    'headless',
    default_value='False',
    description='headless simulation'
  )
  
  use_sim_time_arg = DeclareLaunchArgument(
    'use_sim_time',
    default_value='true',
    description='Use simulation (Gazebo) clock if true'
  )

  world = PathJoinSubstitution([
    FindPackageShare('mirte_gazebo'),
    'worlds',
    'empty.world'
  ])

  robot_description = ParameterValue(
    Command([
      'xacro ', 
      PathJoinSubstitution([
        FindPackageShare('mirte_master_description'), 'urdf', 'mirte_master.xacro'
      ])
    ]),
    value_type=str
  )

  node_robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    name='robot_state_publisher',
    output='screen',
    parameters=[{
        'use_sim_time': use_sim_time,
        'robot_description' : robot_description
    }]
  )

  gz_spawn_entity = Node(
    package='ros_gz_sim',
    executable='create',
    arguments=[
        '-topic', 'robot_description',
        '-x', '0',
        '-y', '0',
        '-z', '0.1',
        '-name', 'mirte_master'
    ],
    output='screen',
  )

  gz_sim = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      PathJoinSubstitution([
        FindPackageShare('ros_ign_gazebo'),
        'launch',
        'ign_gazebo.launch.py',
      ])
    ),
    launch_arguments={'gz_args' : ['-r ', world, ' --verbose']}.items(),
    # launch_arguments={'gz_args' : ['--verbose']}.items(),
  )

  mirte_controllers = Node(
    package='controller_manager',
    executable='spawner',
    arguments=['mirte_base_controller', 'mirte_arm_controller', 'mirte_gripper_controller'],
    parameters=[{
      'use_sim_time': use_sim_time,
    }]
  )

  ros_gz_bridge_params = PathJoinSubstitution([
    FindPackageShare('mirte_gazebo'),
    'config', 
    'ros_gz_bridge.yaml'
  ])

  ros_gz_bridge = Node(
    package="ros_gz_bridge",
    executable="parameter_bridge",
    parameters=[{
        'config_file' : ros_gz_bridge_params,
    }],
    output="screen",
  )

  return LaunchDescription([
    headless_arg,
    use_sim_time_arg,
    gz_sim,
    node_robot_state_publisher,
    gz_spawn_entity,
    mirte_controllers,
    ros_gz_bridge,
  ])