import numpy as np

vec_to_waypoint = np.array([2, -2])
vec_forward = np.array([0, 1])
dot_product = np.dot(vec_to_waypoint, vec_forward)
magnitude1 = np.linalg.norm(vec_to_waypoint)
magnitude2 = np.linalg.norm(vec_forward)
cosine_angle = dot_product / (magnitude1 * magnitude2)
angle = np.degrees(np.arccos(cosine_angle))

print(angle)