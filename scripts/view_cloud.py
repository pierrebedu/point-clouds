#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Show an ASCII PLY point cloud in RViz2.

Publishes the cloud on /bunny as sensor_msgs/PointCloud2 and opens RViz2.
The default file is the Stanford Bunny already in this repo.

ROS 2 Humble has to be on the Python path (source /opt/ros/humble/setup.bash).
If it is not, and Docker can see a display, the same node runs in the
osrf/ros:humble-desktop image.
"""

from __future__ import annotations

import argparse
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

from open_cloud import default_cloud, read_ascii_ply

TOPIC = "/bunny"
FRAME = "bunny"
IMAGE = "osrf/ros:humble-desktop"
FIELDS = ("x", "y", "z", "intensity")


def _message(points: list[dict], names: list[str], stamp):
    from sensor_msgs.msg import PointCloud2, PointField

    used = [name for name in FIELDS if name in names]
    fields = []
    offset = 0
    for name in used:
        fields.append(
            PointField(
                name=name,
                offset=offset,
                datatype=PointField.FLOAT32,
                count=1,
            )
        )
        offset += 4

    blob = bytearray()
    for point in points:
        for name in used:
            blob += struct.pack("<f", point[name])

    msg = PointCloud2()
    msg.header.frame_id = FRAME
    msg.header.stamp = stamp
    msg.height = 1
    msg.width = len(points)
    msg.fields = fields
    msg.is_bigendian = False
    msg.point_step = offset
    msg.row_step = offset * len(points)
    msg.data = bytes(blob)
    msg.is_dense = True
    return msg


def _publish_frame(node) -> None:
    """Make the fixed frame exist, so RViz2 does not warn about a missing TF."""
    from geometry_msgs.msg import TransformStamped
    from tf2_ros import StaticTransformBroadcaster

    transform = TransformStamped()
    transform.header.stamp = node.get_clock().now().to_msg()
    transform.header.frame_id = FRAME
    transform.child_frame_id = "bunny_points"
    transform.transform.rotation.w = 1.0
    broadcaster = StaticTransformBroadcaster(node)
    broadcaster.sendTransform(transform)
    node.frame_broadcaster = broadcaster


def _rviz_config() -> Path:
    return Path(__file__).resolve().parent.parent / "rviz" / "bunny.rviz"


def _run_local(path: Path, open_rviz: bool) -> int:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
    from sensor_msgs.msg import PointCloud2

    try:
        cloud = read_ascii_ply(path)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"cannot read file: {error}", file=sys.stderr)
        return 1

    rclpy.init()
    node = Node("view_cloud")
    qos = QoSProfile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        history=HistoryPolicy.KEEP_LAST,
        depth=5,
    )
    publisher = node.create_publisher(PointCloud2, TOPIC, qos)
    _publish_frame(node)
    template = _message(
        cloud["points"],
        cloud["names"],
        node.get_clock().now().to_msg(),
    )

    def publish() -> None:
        template.header.stamp = node.get_clock().now().to_msg()
        publisher.publish(template)

    publish()
    node.create_timer(1.0, publish)
    print(
        f"publishing {len(cloud['points'])} points on {TOPIC} "
        f"(frame {FRAME}) from {path}",
        flush=True,
    )

    rviz = None
    if open_rviz:
        rviz_bin = shutil.which("rviz2")
        if rviz_bin is None:
            print(
                f"rviz2 was not found. The cloud is still on {TOPIC}.",
                file=sys.stderr,
            )
        else:
            rviz = subprocess.Popen([rviz_bin, "-d", str(_rviz_config())])
            print(
                "RViz2 is open. Fixed frame: bunny. Ctrl-C stops the view.",
                flush=True,
            )

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.2)
            if rviz is not None and rviz.poll() is not None:
                break
    except KeyboardInterrupt:
        pass
    finally:
        if rviz is not None and rviz.poll() is None:
            rviz.terminate()
        node.destroy_node()
        rclpy.try_shutdown()
    return 0


def _docker_file_args(path: Path) -> list[str] | None:
    repo = Path(__file__).resolve().parent.parent
    resolved = path.resolve()
    if resolved == default_cloud().resolve():
        return []
    try:
        relative = resolved.relative_to(repo)
    except ValueError:
        print(
            "Without a local ROS 2 install, the file has to stay inside this repo.",
            file=sys.stderr,
        )
        return None
    return [str(relative)]


def _run_in_docker(extra: list[str]) -> int:
    if shutil.which("docker") is None:
        print(
            "ROS 2 is not on this Python path, and docker was not found.\n"
            "Source ROS 2 Humble, then run this script again:\n"
            "  source /opt/ros/humble/setup.bash",
            file=sys.stderr,
        )
        return 1
    if not os.environ.get("DISPLAY"):
        print(
            "ROS 2 is not on this Python path, and there is no display for RViz2.\n"
            "Source ROS 2 Humble, then run this script again:\n"
            "  source /opt/ros/humble/setup.bash",
            file=sys.stderr,
        )
        return 1

    repo = Path(__file__).resolve().parent.parent
    print(
        f"ROS 2 is not installed here. Opening RViz2 in {IMAGE}. "
        "The first run downloads the image."
    )
    command = [
        "docker",
        "run",
        "--rm",
        "-i",
        "--user",
        f"{os.getuid()}:{os.getgid()}",
        "-e",
        "VIEW_CLOUD_IN_ROS=1",
        "-e",
        "HOME=/tmp",
        "-e",
        "QT_QPA_PLATFORM=xcb",
        "-e",
        "QT_X11_NO_MITSHM=1",
        "-e",
        "LIBGL_ALWAYS_SOFTWARE=1",
        "-e",
        f"DISPLAY={os.environ['DISPLAY']}",
        "-e",
        "PYTHONDONTWRITEBYTECODE=1",
        "-e",
        "PYTHONUNBUFFERED=1",
        "-v",
        "/tmp/.X11-unix:/tmp/.X11-unix",
        "-v",
        f"{repo}:/work:ro",
        "-w",
        "/work",
        "--entrypoint",
        "bash",
        IMAGE,
        "-lc",
        "source /opt/ros/humble/setup.bash && "
        "exec python3 /work/scripts/view_cloud.py \"$@\"",
        "bash",
        *extra,
    ]
    return subprocess.call(command)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Publish an ASCII PLY cloud and open it in RViz2."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=default_cloud(),
        help="PLY file (default: data/bunny/bun_zipper_res2.ply)",
    )
    parser.add_argument(
        "--no-rviz",
        action="store_true",
        help="only publish the cloud",
    )
    args = parser.parse_args(argv)
    path = args.path
    if not path.is_file():
        print(f"file not found: {path}", file=sys.stderr)
        return 1

    try:
        import rclpy  # noqa: F401
    except ImportError:
        rclpy = None

    if rclpy is None:
        if os.environ.get("VIEW_CLOUD_IN_ROS") == "1":
            print("ROS 2 Python packages are missing in this environment.", file=sys.stderr)
            return 1
        extra = _docker_file_args(path)
        if extra is None:
            return 1
        if args.no_rviz:
            extra.append("--no-rviz")
        return _run_in_docker(extra)

    return _run_local(path, open_rviz=not args.no_rviz)


if __name__ == "__main__":
    raise SystemExit(main())
