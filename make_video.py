import argparse
import subprocess
from pathlib import Path
from natsort import natsorted

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helper")
    parser.add_argument("-p", "--path", type=Path, default=Path("."))
    parser.add_argument("-f", "--find_frames", action="store_true")
    parser.add_argument("-e", "--elapsed", type=int)
    parser.add_argument("-r", "--rate", type=int)
    parser.add_argument("-c", "--crf", type=int)

    args = parser.parse_args()

    print(args)

    path0 = args.path
    path = path0

    if args.find_frames:
        path /= "simu/rec"

        if args.elapsed is not None:
            elapsed = args.elapsed
        else:
            dirs = natsorted(path.iterdir())
            elapsed = dirs[0]

        path /= f"{elapsed}/frames"

    print(f"Extracting from {path}")

    frames = [
        f for f in natsorted(path.iterdir()) if f.is_file() and f.suffix[1:] == "png"
    ]

    print(f"Found {len(frames)} frames")

    concat = path / "concat.txt"
    with concat.open("w") as buf:
        for frame in frames:
            buf.write(f"file '{frame.name}'\n")

    print(f"Wrote concat file at {concat}")

    # rate (fps) can be 60, 140, ...
    # crf can be 18

    rate = f"-r {args.rate}" if args.rate is not None else ""
    crf = f"-crf {args.crf}" if args.crf is not None else ""

    video = path / "video.mp4"
    subprocess.call(
        f"ffmpeg -y -loglevel error -f concat {rate} -safe 0 -i '{concat}' -vf 'yadif, format=yuv420p' -c:v libx264 {crf} '{video}'",
        cwd=path,
        shell=True,
    )

    concat.rename(path0 / concat.name)
    video.rename(path0 / video.name)

    print(f"Wrote video {video}")