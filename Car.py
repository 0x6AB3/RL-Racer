import pygame
import math
import random

class Car:
    def __init__(self, x, y, angle=0, color=(255, 0, 0), gene=None):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.speed = 0
        self.acceleration = 0.5  # Increased acceleration
        self.deceleration = 0.2
        self.turn_speed = 5    # Increased turn speed
        self.friction = 0.95   # Reduced friction
        self.width = 40
        self.height = 20

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, self.width, self.height))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.has_collided_with_wall = False
        self.passed_gates = set() # Store indices of passed gates
        self.score = 0 # Number of gates passed
        self.next_gate_index = 0
        self.time_taken = 0 # Time taken to reach current score
        self.distance_traveled = 0.0 # New attribute for tracking distance
        self.gene = gene if gene is not None else []
        self.current_gene_index = 0
        self.is_active = True
        self.old_x = float(x)
        self.old_y = float(y)

    def reset(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.speed = 0
        self.has_collided_with_wall = False
        self.passed_gates = set()
        self.score = 0
        self.next_gate_index = 0
        self.current_gene_index = 0
        self.is_active = True
        self.old_x = float(x)
        self.old_y = float(y)

    def get_corners(self):
        corners = []
        half_width = self.width / 2
        half_height = self.height / 2
        
        # Top-left
        corners.append((self.x - half_width, self.y - half_height))
        # Top-right
        corners.append((self.x + half_width, self.y - half_height))
        # Bottom-right
        corners.append((self.x + half_width, self.y + half_height))
        # Bottom-left
        corners.append((self.x - half_width, self.y + half_height))

        # Rotate corners
        rotated_corners = []
        for x, y in corners:
            x_prime = self.x + (x - self.x) * math.cos(math.radians(self.angle)) - (y - self.y) * math.sin(math.radians(self.angle))
            y_prime = self.y + (x - self.x) * math.sin(math.radians(self.angle)) + (y - self.y) * math.cos(math.radians(self.angle))
            rotated_corners.append((x_prime, y_prime))
        return rotated_corners

    def get_distance_to_wall(self, track, angle_offset=0):
        # Cast a ray in a specific direction relative to the car's heading
        ray_length = 500  # Max distance to check for walls
        
        # Calculate the absolute angle of the ray
        absolute_ray_angle = self.angle + angle_offset

        # Check for intersection with track boundaries
        intersection_point = track.get_ray_intersection_with_track_boundary((self.x, self.y), absolute_ray_angle, ray_length)
        
        if intersection_point:
            distance = math.sqrt((self.x - intersection_point[0])**2 + (self.y - intersection_point[1])**2)
            return distance
        return ray_length # No wall detected within ray_length

    def update(self, screen_width, screen_height, track, accelerate, decelerate, turn_left, turn_right):
        # Store position before update for gate collision check
        self.old_x, self.old_y = self.x, self.y

        if accelerate:
            self.speed += self.acceleration
        if decelerate:
            self.speed -= self.deceleration
        if turn_left:
            self.angle += self.turn_speed
        if turn_right:
            self.angle -= self.turn_speed

        # Apply friction
        self.speed *= self.friction

        # Calculate velocity components
        velocity_x = self.speed * math.cos(math.radians(self.angle))
        velocity_y = self.speed * -math.sin(math.radians(self.angle)) # Negative because y is inverted

        # Update car's float position
        self.x += velocity_x
        self.y += velocity_y
        self.time_taken += 1 # Increment time taken
        self.distance_traveled += math.sqrt((self.x - self.old_x)**2 + (self.y - self.old_y)**2) # Update distance traveled

        # Update the car's rect for drawing
        self.rect.center = (int(self.x), int(self.y))

        # Check for collisions with track boundaries
        corners = self.get_corners()
        for corner in corners:
            if not track.is_on_track(corner):
                self.has_collided_with_wall = True # Set flag on collision with track boundary
                self.is_active = False # Car becomes inactive on collision
                break

        self.check_gate_collision(track)

    def line_segment_intersect(self, p1, p2, p3, p4):
        # Returns true if line segments p1p2 and p3p4 intersect
        # p1, p2 are points of the first line segment
        # p3, p4 are points of the second line segment

        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

    def check_gate_collision(self, track):
        if self.next_gate_index < len(track.gates):
            gate = track.gates[self.next_gate_index]
            gate_p1, gate_p2 = gate

            # Get the car's current position and previous position
            car_current_pos = (self.x, self.y)
            car_prev_pos = (self.old_x, self.old_y)

            # Check if the line segment from car_prev_pos to car_current_pos intersects the gate
            if self.line_segment_intersect(car_prev_pos, car_current_pos, gate_p1, gate_p2):
                self.score += 1
                self.next_gate_index = (self.next_gate_index + 1) % len(track.gates) # Loop gates
        
        # Update old_x and old_y for the next frame
        self.old_x = self.x
        self.old_y = self.y

    def decide_actions(self, track):
        # Get distances to walls in different directions
        distance_front = self.get_distance_to_wall(track, 0) # Directly in front
        distance_left = self.get_distance_to_wall(track, 45) # 45 degrees to the left
        distance_right = self.get_distance_to_wall(track, -45) # 45 degrees to the right

        accelerate = True
        decelerate = False
        turn_left = False
        turn_right = False

        # Simple wall avoidance: if too close to a wall, turn away
        # Prioritize avoiding immediate front collision
        if distance_front < 80: # If very close to front wall
            accelerate = False
            if distance_left > distance_right: # Turn towards the more open side
                turn_left = True
            else:
                turn_right = True
        elif distance_front < 150: # If somewhat close to front wall
            if distance_left > distance_right: # Turn towards the more open side
                turn_left = True
            else:
                turn_right = True
        
        # Gate optimization: try to steer towards the next gate, but don't override wall avoidance
        if not (turn_left or turn_right) and self.next_gate_index < len(track.gates):
            next_gate = track.gates[self.next_gate_index]
            gate_center_x = (next_gate[0][0] + next_gate[1][0]) / 2
            gate_center_y = (next_gate[0][1] + next_gate[1][1]) / 2

            # Calculate angle to the next gate
            angle_to_gate = math.degrees(math.atan2(self.y - gate_center_y, gate_center_x - self.x))
            
            # Normalize angles to be within -180 to 180
            relative_angle = (angle_to_gate - self.angle + 360) % 360
            if relative_angle > 180:
                relative_angle -= 360

            # Adjust turning based on angle to gate
            if relative_angle > 10: # Gate is to the left
                turn_left = True
            elif relative_angle < -10: # Gate is to the right
                turn_right = True

        # If gene runs out, car stops
        if self.current_gene_index >= len(self.gene):
            return False, False, False, False

        # For now, still use the gene for actions, but allow the above logic to override
        # In a full GA, the gene would evolve to incorporate these behaviors.
        gene_accelerate, gene_decelerate, gene_turn_left, gene_turn_right = self.gene[self.current_gene_index]
        self.current_gene_index += 1

        # Combine gene actions with AI actions (AI overrides if necessary)
        final_accelerate = accelerate or gene_accelerate
        final_decelerate = decelerate or gene_decelerate
        final_turn_left = turn_left or gene_turn_left
        final_turn_right = turn_right or gene_turn_right

        # If the AI suggests turning, but the gene also suggests turning in the opposite direction,
        # prioritize the AI's suggestion for safety, but allow the gene to influence acceleration.
        if (turn_left and gene_turn_right) or (turn_right and gene_turn_left):
            final_accelerate = gene_accelerate # Let gene decide acceleration in this case
            final_decelerate = gene_decelerate

        return final_accelerate, final_decelerate, final_turn_left, final_turn_right

    def draw(self, screen):
        rotated_car = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated_car.get_rect(center=self.rect.center)
        screen.blit(rotated_car, rotated_rect.topleft)