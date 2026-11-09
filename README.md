# Point clouds

A small repo for learning point clouds on a CPU, without a heavy dataset.

Planned path:

1. **Open** a cloud and read what it contains. This is the current script.
2. **View** the cloud.
3. **Segment** an object in a scene.
4. **ICP**: align a partial scan to a known 3D model.

Only the first step is implemented.

## Dataset

[Stanford Bunny](https://graphics.stanford.edu/data/3Dscanrep/), from the Stanford 3D Scanning Repository (Stanford University Computer Graphics Laboratory, 1996). It is the usual reference model in 3D geometry: small, public, and already used for reconstruction and registration.

The file in this repo is `data/bunny/bun_zipper_res2.ply`. It keeps Stanford's own terms (`data/bunny/NOTICE`) and is not part of the CC0 dedication that covers the rest of this repository.

- reconstructed bunny, decimated `res2` version;
- 8,171 points, about 650 KB;
- the full reconstruction (`bun_zipper.ply`) has 35,947 points. `res2` is enough to learn on without loading the machine.

Vertices carry `x y z`, plus `confidence` and `intensity` from the scanner. The file also contains faces: it is a mesh. The script treats the vertices as a point cloud and only reports the face count.

This mesh is the known 3D model for the later ICP step. The original partial scans (`bun000`, `bun045`, and so on) stay on the Stanford site until that step. The bunny is a single object: segmenting a scene (a table, several objects) will use another cloud of the same small size.

## Open the cloud

Python 3 and the standard library only. There is no window: viewing is the next step.

```bash
python3 scripts/open_cloud.py
```

Another ASCII PLY file:

```bash
python3 scripts/open_cloud.py path/to/cloud.ply
```

The output is the point count, the properties, the other elements in the file, then the min, max, and mean of `x`, `y`, and `z`.

## License

The original code and documentation are dedicated to the public domain under [CC0 1.0 Universal](LICENSE). You can copy, modify, and redistribute them for any purpose, including commercial use, without asking permission and without attribution.

The Stanford Bunny mesh is the exception. Stanford allows research use and free redistribution when the Stanford Computer Graphics Laboratory is credited, and asks for permission before commercial use or inclusion in a product for sale. See `data/bunny/NOTICE`.
