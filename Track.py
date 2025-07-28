import pygame
import math

class Track:
    def __init__(self, width, height, car_width):
        self.width = width
        self.height = height
        self.track_width = car_width * 2.5  # Ensure ample space for the car
        self.outer_points = []
        self.inner_points = []
        self.center_points = []
        self.gates = [] # List to store gate coordinates
        self.generate_track()

    def generate_track(self):
        center_x, center_y = self.width / 2, self.height / 2
        
        # Define the dimensions of the outer and inner ellipses
        outer_radius_x = self.width / 2 - 60  # Margin from screen edge
        outer_radius_y = self.height / 2 - 60 # Margin from screen edge
        inner_radius_x = outer_radius_x - self.track_width
        inner_radius_y = outer_radius_y - self.track_width

        # Generate points for the ellipses
        for i in range(361):
            angle = math.radians(i)
            
            # Outer boundary
            outer_x = center_x + outer_radius_x * math.cos(angle)
            outer_y = center_y + outer_radius_y * math.sin(angle)
            self.outer_points.append((outer_x, outer_y))
            
            # Inner boundary
            inner_x = center_x + inner_radius_x * math.cos(angle)
            inner_y = center_y + inner_radius_y * math.sin(angle)
            self.inner_points.append((inner_x, inner_y))

            

            # Center line for starting position
            center_track_x = center_x + ((outer_radius_x + inner_radius_x) / 2) * math.cos(angle)
            center_track_y = center_y + ((outer_radius_y + inner_radius_y) / 2) * math.sin(angle)
            self.center_points.append((center_track_x, center_track_y))

        # Generate gates
        num_gates = 32
        for i in range(num_gates):
            index = int(len(self.center_points) / num_gates * i)
            gate_center = self.center_points[index]
            
            # Calculate gate orientation (perpendicular to track center line)
            if index + 1 < len(self.center_points):
                next_point = self.center_points[index + 1]
            else:
                next_point = self.center_points[0] # Loop back to start

            dx = next_point[0] - gate_center[0]
            dy = next_point[1] - gate_center[1]
            
            # Angle perpendicular to the track segment
            gate_angle = math.atan2(dy, dx) + math.pi / 2 # Add 90 degrees

            # Calculate gate endpoints
            gate_half_width = self.track_width / 2
            gate_p1_x = gate_center[0] + gate_half_width * math.cos(gate_angle)
            gate_p1_y = gate_center[1] + gate_half_width * math.sin(gate_angle)
            gate_p2_x = gate_center[0] - gate_half_width * math.cos(gate_angle)
            gate_p2_y = gate_center[1] - gate_half_width * math.sin(gate_angle)
            
            self.gates.append(((gate_p1_x, gate_p1_y), (gate_p2_x, gate_p2_y)))

    def point_in_polygon(self, point, polygon):
        x, y = point
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def is_on_track(self, point):
        # A point is on the track if it's inside the outer boundary but outside the inner one.
        return self.point_in_polygon(point, self.outer_points) and not self.point_in_polygon(point, self.inner_points)

    def get_ray_intersection_with_track_boundary(self, start_point, angle_degrees, ray_length):
        # Calculate the end point of the ray
        rad_angle = math.radians(angle_degrees)
        end_point_x = start_point[0] + ray_length * math.cos(rad_angle)
        end_point_y = start_point[1] - ray_length * math.sin(rad_angle) # Pygame y-axis is inverted
        
        p1 = start_point
        p2 = (end_point_x, end_point_y)

        # Check intersection with outer boundary
        intersection = self._get_line_segment_polygon_intersection(p1, p2, self.outer_points)
        if intersection:
            return intersection
        
        # Check intersection with inner boundary
        intersection = self._get_line_segment_polygon_intersection(p1, p2, self.inner_points)
        if intersection:
            return intersection
        
        return None

    def _get_line_segment_polygon_intersection(self, p1, p2, polygon):
        # Helper to find the closest intersection point of a line segment with a polygon
        closest_intersection = None
        min_dist_sq = float('inf')

        for i in range(len(polygon)):
            p3 = polygon[i]
            p4 = polygon[(i + 1) % len(polygon)]
            
            intersection = self._get_line_segment_intersection(p1, p2, p3, p4)
            if intersection:
                dist_sq = (p1[0] - intersection[0])**2 + (p1[1] - intersection[1])**2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_intersection = intersection
        return closest_intersection

    def _get_line_segment_intersection(self, p1, p2, p3, p4):
        # Helper to find the intersection point of two line segments
        # p1, p2: segment 1
        # p3, p4: segment 2

        s1_x, s1_y = p2[0] - p1[0], p2[1] - p1[1]
        s2_x, s2_y = p4[0] - p3[0], p4[1] - p3[1]

        denominator = (-s2_x * s1_y + s1_x * s2_y)
        if denominator == 0: # Parallel lines
            return None

        s = (-s1_y * (p1[0] - p3[0]) + s1_x * (p1[1] - p3[1])) / denominator
        t = ( s2_x * (p1[1] - p3[1]) - s2_y * (p1[0] - p3[0])) / denominator

        if 0 <= s <= 1 and 0 <= t <= 1:
            # Intersection detected
            intersection_x = p1[0] + (t * s1_x)
            intersection_y = p1[1] + (t * s1_y)
            return (intersection_x, intersection_y)

        return None

    def draw(self, screen):
        # Draw the track surface
        pygame.draw.polygon(screen, (128, 128, 128), self.outer_points) # Gray for the track
        pygame.draw.polygon(screen, (30, 30, 30), self.inner_points)   # Dark gray for the infield

        # Draw a finish line
        start_line_p1 = self.outer_points[0]
        start_line_p2 = self.inner_points[0]
        pygame.draw.line(screen, (255, 255, 255), start_line_p1, start_line_p2, 5)

        # Draw gates
        for gate in self.gates:
            pygame.draw.line(screen, (0, 255, 0), gate[0], gate[1], 2)