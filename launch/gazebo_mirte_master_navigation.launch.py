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
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable,PathJoinSubstitution
from launch.actions import SetEnvironmentVariable


def generate_launch_description():
    pkg_robocup_home_simulation = get_package_share_directory(
        'robocup_home_simulation')
    robocup_home_world_path = os.path.join(
        pkg_robocup_home_simulation,
        'worlds',
        'KRR_Course_Small_house_added_objects.world')
    
    pkg_mirte_gazebo = get_package_share_directory(
        'mirte_gazebo')
    mirte_gazebo_launch_path = os.path.join(
        pkg_mirte_gazebo,
        'launch',
        'gazebo_mirte_master_empty.launch.xml')
    mirte_gazebo_launch = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(mirte_gazebo_launch_path),
        launch_arguments={
            'world': robocup_home_world_path,
        }.items()
    )

    pkg_mirte_navigation = get_package_share_directory(
        'mirte_navigation')
    mirte_navigation_launch_path = os.path.join(
        pkg_mirte_navigation,
        'launch',
        'robot_navigation.launch.py')

    mirte_navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(mirte_navigation_launch_path)
    )
    
    pkg_plasys_house_world = get_package_share_directory(
        'plasys_house_world')
    plasys_house_world_models = os.path.join(
        pkg_plasys_house_world,
        'models')

    pkg_aws_robomaker_small_house_world = get_package_share_directory(
        'aws_robomaker_small_house_world')
    aws_robomaker_small_house_world_models = os.path.join(
        pkg_aws_robomaker_small_house_world,
        'models')
    
    pkg_sdf_models = get_package_share_directory(
        'sdf_models')


    pkg_mirte_skills = get_package_share_directory(
            'krr_mirte_skills')
    pkg_mirte_skills_launch_path = os.path.join(
        pkg_mirte_skills,
        'launch',
        'mirte_skills.launch.xml')
    mirte_skills_launch = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(pkg_mirte_skills_launch_path),
        launch_arguments={
           
        }.items()
    )

    mirte_laser_filters = Node(
        package="laser_filters",
        executable="scan_to_scan_filter_chain",
        parameters=[
            PathJoinSubstitution([
                get_package_share_directory("mirte_gazebo"),
                "config", "range_filter.yaml",
            ])],
    )

    return LaunchDescription([
        SetEnvironmentVariable(name='GAZEBO_MODEL_PATH', value=[
            EnvironmentVariable('GAZEBO_MODEL_PATH'),
            ':',plasys_house_world_models,
            ':',aws_robomaker_small_house_world_models,
            ':',pkg_sdf_models]),
        mirte_navigation_launch,
        mirte_skills_launch,
        mirte_laser_filters,
        mirte_gazebo_launch,
    ])
