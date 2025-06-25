import os
import subprocess
import sys
import shutil
def convert_svg_to_png(svg_file_path, output_dir):
    """
    Converts a single SVG file to a PNG file using rsvg-convert.
    This function is designed to be run in a separate thread/process.
    """
    base_name = os.path.basename(svg_file_path).replace(".svg", "")
    png_file_path = os.path.join(output_dir, f"{base_name}.png")
    
    try:
        subprocess.run(
            ["rsvg-convert", "--format=png", "--output", png_file_path, svg_file_path],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error converting SVG to PNG for {svg_file_path}: {e}", file=sys.stderr)
        print(f"Stdout: {e.stdout}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        raise
    except FileNotFoundError:
        print("Error: 'rsvg-convert' command not found. Please ensure rsvg-convert is installed and in your system's PATH.", file=sys.stderr)
        raise




def check_tool_availability(*tool_names: str, print_errors = True) -> bool:
    """
    Checks if a given command-line tool is available in the system's PATH.

    :param *tool_name: The names of the executable to check (e.g., "ffmpeg", "rsvg-convert").
    :type tool_name: str
    :param exit_with_error: If True, exits the process with an error message when the function would return False.
    :type exit_with_error: bool
    :returns: True if the tool is found in PATH, False otherwise.
    :rtype: bool
    """

    all_tools_available = True
    for tool_name in tool_names:
        tool_path = shutil.which(tool_name)        
        if not tool_path:
            if print_errors:
                print(f"'{tool_name}' not found in system PATH. Please ensure it is installed and added to your PATH.", file=sys.stderr)
            all_tools_available = False
            
    if all_tools_available:
        return True
    else:
        return False
