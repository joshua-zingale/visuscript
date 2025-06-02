# import numpy as np

# def ellipse_arc_length(a, b, start_angle_deg, end_angle_deg, num_segments=1000):
#     """
#     Approximates the arc length of an ellipse between two angles.

#     Args:
#         a (float): Semi-major axis of the ellipse.
#         b (float): Semi-minor axis of the ellipse.
#         start_angle_deg (float): Starting angle in degrees.
#         end_angle_deg (float): Ending angle in degrees.
#         num_segments (int): Number of segments to use for numerical integration.
#                            Higher values give more accurate results.

#     Returns:
#         float: Approximate arc length.
#     """
#     start_angle_rad = np.deg2rad(start_angle_deg)
#     end_angle_rad = np.deg2rad(end_angle_deg)
#     angles = np.linspace(start_angle_rad, end_angle_rad, num_segments + 1)
#     d_theta = (end_angle_rad - start_angle_rad) / num_segments

#     arc_length = 0.0
#     for i in range(num_segments):
#         theta1 = angles[i]
#         theta2 = angles[i+1]

#         # Parametric equations of an ellipse:
#         # x(theta) = a * cos(theta)
#         # y(theta) = b * sin(theta)

#         dx_dtheta1 = -a * np.sin(theta1)
#         dy_dtheta1 = b * np.cos(theta1)
#         ds1 = np.sqrt(dx_dtheta1**2 + dy_dtheta1**2)

#         dx_dtheta2 = -a * np.sin(theta2)
#         dy_dtheta2 = b * np.cos(theta2)
#         ds2 = np.sqrt(dx_dtheta2**2 + dy_dtheta2**2)

#         arc_length += (ds1 + ds2) / 2 * d_theta  # Trapezoidal rule

#     return arc_length