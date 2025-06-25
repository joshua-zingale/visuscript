"""Creates a video file from an input stream of plain-text SVG files.
"""
import sys
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from visuscript.cli.utility import convert_svg_to_png, check_tool_availability

def main():
    if len(sys.argv) < 3:
        print("Usage: python visuscript_animate.py <fps> <output_filename>", file=sys.stderr)
        sys.exit(1)

    if not check_tool_availability('rsvg-convert', 'ffmpeg', print_errors=True):
        sys.exit(1)

    frame_rate = sys.argv[1]
    output_file = sys.argv[2]

    svg_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        counter = 1
        for svg_blob in sys.stdin:
            svg_file_path = os.path.join(temp_dir, f"frame_{counter:09d}.svg")
            try:
                with open(svg_file_path, "w", encoding="utf-8") as f:
                    f.write(svg_blob)
                svg_files.append(svg_file_path)
                counter += 1
            except IOError as e:
                print(f"Error writing SVG to file {svg_file_path}: {e}", file=sys.stderr)
                sys.exit(1)
        
        if not svg_files:
            print("No SVG data received from stdin. Exiting.", file=sys.stderr)
            sys.exit(0)


        num_cpus = os.cpu_count() if os.cpu_count() else 1
        print(f"Using {num_cpus} parallel processes for SVG to PNG conversion.", file=sys.stderr)

        with ThreadPoolExecutor(max_workers=num_cpus) as executor:
            # Submit all conversion tasks
            future_to_svg = {executor.submit(convert_svg_to_png, svg_file, temp_dir): svg_file for svg_file in svg_files}
            
            for future in as_completed(future_to_svg):
                svg_file = future_to_svg[future]
                try:
                    future.result() # Get result to check for exceptions
                except Exception as exc:
                    print(f'{os.path.basename(svg_file)} generated an exception: {exc}', file=sys.stderr)
                    sys.exit(1) # Exit on first conversion error

        print(f"Successfully converted {len(svg_files)} frames to PNG.", file=sys.stderr)

        png_pattern = os.path.join(temp_dir, "frame_%09d.png")
        
        ffmpeg_command = [
            "ffmpeg",
            "-framerate", frame_rate,
            "-i", png_pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            output_file,
            "-hide_banner",
            "-loglevel", "warning"
        ]
        
        print(f"Generating video: {output_file}...", file=sys.stderr)
        try:
            subprocess.run(
                ffmpeg_command,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error creating video with ffmpeg: {e}", file=sys.stderr)
            print(f"Stdout: {e.stdout}", file=sys.stderr)
            print(f"Stderr: {e.stderr}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()

