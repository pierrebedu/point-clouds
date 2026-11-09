# Point clouds

A small repo for learning point clouds on a CPU, without a heavy dataset.

Two branches, and one bonus:

*   **`main`** — open one cloud and look at it, segment something, ...
*   **`video`** — track a person through a short sequence.
*   **ICP**, later — align one cloud to another. Not required for the two steps above.

Everything is a point cloud. ROS 2 is the viewer: RViz2 displays a `sensor_msgs/PointCloud2`, for one frozen cloud and for a cloud that changes over time.

## Clouds

The smallest clouds that still show the idea.

### Static — the bunny (`main`)

[Stanford Bunny](https://graphics.stanford.edu/data/3Dscanrep/), file `data/bunny/bun_zipper_res2.ply`, already in this repo.

*   one object, no time;
*   decimated reconstruction (`res2`): 8,171 points, about 650 KB;
*   the full reconstruction has 35,947 points. `res2` is enough here.

Vertices carry `x y z`, plus `confidence` and `intensity`. The file also contains faces: it is a mesh. The script reads the vertices as a point cloud and only reports the face count.

### People walking — `walking_static` (`video`)

[TUM RGB-D](https://cvg.cit.tum.de/data/datasets/rgbd-dataset/download), sequence `freiburg3/walking_static`.

*   the camera stays still and two people walk through an office;
*   about 25 seconds, archive about 0.48 GB;
*   RGB images and depth images, not a PLY. Each depth frame is one point cloud.

The archive is not in this repo. The published ground truth is the camera trajectory, not a track of each person. The people are the moving part of the cloud; following one of them is the work of the `video` branch.

## Open (`main`)

This step exists. Python 3 and the standard library only.

```bash
python3 scripts/open_cloud.py
```

Another ASCII PLY file:

```bash
python3 scripts/open_cloud.py path/to/cloud.ply
```

The output is the point count, the properties, the other elements in the file, then the min, max, and mean of `x`, `y`, and `z`.

## View (`main`)

RViz2 is the window. The script reads the bunny and publishes it as a `sensor_msgs/PointCloud2` on `/bunny`, in the frame `bunny`, then opens RViz2 on that topic.

```bash
python3 scripts/view_cloud.py
```

Another ASCII PLY file:

```bash
python3 scripts/view_cloud.py path/to/cloud.ply
```

Ctrl-C closes the view. With ROS 2 Humble already sourced, the script uses that install. Otherwise, if Docker can see a display, it runs the same node in `osrf/ros:humble-desktop` (the first run downloads the image). The same display is what `video` reuses when the cloud starts to move.

## Track (`video`)

On the `video` branch, play `walking_static` as a stream of point clouds and follow one person from frame to frame. The sensor does not move, so a change in the cloud is someone walking.

Nothing on this branch is written yet.

## ICP (bonus)

Align one cloud to another: a partial view to the bunny, or one frame of the walk to the next. Useful once a cloud can be opened, shown, and followed. Not part of the path above.

## License

The code and documentation are dedicated to the public domain under [CC0 1.0 Universal](LICENSE). You can copy, modify, and redistribute them for any purpose, including commercial use, without asking permission and without attribution.