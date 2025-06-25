"""Creates a multi-page PDF from an input stream of plain-text SVG files.
"""

import sys
import os
import subprocess
import tempfile
import glob
from visuscript.cli.utility import check_tool_availability

def main():
    if len(sys.argv) < 2:
        print("Usage: python visuscript_slideshow.py <output_filename>", file=sys.stderr)
        sys.exit(1)

    if not check_tool_availability('rsvg-convert', print_errors=True):
        sys.exit(1)

    output_file = sys.argv[1]

    with tempfile.TemporaryDirectory() as temp_dir:
        counter = 1
        svg_file_paths = []

        for svg_blob in sys.stdin:
            svg_file_path = os.path.join(temp_dir, f"temp_{counter:09d}.svg")
            try:
                with open(svg_file_path, "w", encoding="utf-8") as f:
                    f.write(svg_blob)
                svg_file_paths.append(svg_file_path)
                counter += 1
            except IOError as e:
                print(f"Error writing SVG to file {svg_file_path}: {e}", file=sys.stderr)
                sys.exit(1)
        
        if not svg_file_paths:
            print("No SVG data received from stdin for slideshow. Exiting.", file=sys.stderr)
            sys.exit(0)

        print(f"Received {len(svg_file_paths)} SVG frames for slideshow. Converting to PDF...", file=sys.stderr)

       
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except OSError as e:
                print(f"Error removing existing output file {output_file}: {e}", file=sys.stderr)
                sys.exit(1)

        rsvg_command = [
            "rsvg-convert",
            "-f", "pdf",
            *sorted(glob.glob(os.path.join(temp_dir, "temp_*.svg"))), 
            "-o", output_file
        ]
        
        try:
            subprocess.run(
                rsvg_command,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error creating PDF with rsvg-convert: {e}", file=sys.stderr)
            print(f"Stdout: {e.stdout}", file=sys.stderr)
            print(f"Stderr: {e.stderr}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()

