import pygame
import math
import random
from Car import Car
from Track import Track

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")

# Colors
BLACK = (0, 0, 0)

# Create a track
# We need to know the car's width to create the track with appropriate spacing
# Let's define a temporary car_width for now
temp_car_width = 40 # Assuming car width is 40
track = Track(SCREEN_WIDTH, SCREEN_HEIGHT, temp_car_width)

# Calculate starting angle
p1 = track.center_points[0]
p2 = track.center_points[1]
dx = p2[0] - p1[0]
dy = p2[1] - p1[1]
start_angle = math.degrees(math.atan2(-dy, dx))



NUM_CARS = 10

# Colors for cars
CAR_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (255, 128, 0),  # Orange
    (128, 0, 255),  # Purple
    (0, 128, 255),  # Light Blue
    (139, 69, 19)   # Brown
]

# Function to initialize/reset cars for a new generation
def reset_cars(current_cars=None):
    new_cars = []
    global last_best_score, generations_since_last_improvement, gene_length

    if current_cars:
        # Sort cars by score to select the best
        current_cars.sort(key=lambda car: (car.score, car.distance_traveled), reverse=True)
        best_car = current_cars[0]
        print(f"Best car score: {best_car.score} gates, {best_car.distance_traveled:.2f} distance")

        # Adjust score to heavily penalize not passing gates and reward faster completion
        adjusted_score = best_car.score * 1000000 - best_car.time_taken # Gates are worth much more, time taken is subtracted

        if adjusted_score > last_best_score:
            last_best_score = adjusted_score
            generations_since_last_improvement = 0
        else:
            generations_since_last_improvement += 1

        # Adjust mutation rate based on improvement
        base_mutation_rate = 0.05
        max_mutation_rate = 0.7 # Increased max mutation rate
        mutation_increase_factor = 0.05 # Increased how much mutation increases per stuck generation

        dynamic_mutation_rate = base_mutation_rate + (generations_since_last_improvement * mutation_increase_factor)
        if generations_since_last_improvement >= 1: # Trigger earlier
            dynamic_mutation_rate += 0.1 # Additional jump for sustained lack of improvement
        if dynamic_mutation_rate > max_mutation_rate:
            dynamic_mutation_rate = max_mutation_rate

        # If stuck for too long, increase preserved mutation rate slightly
        mutation_rate_preserved = 0.02 # Increased preserved mutation rate
        if generations_since_last_improvement > 1: # Trigger earlier
            mutation_rate_preserved = 0.05 # Increase preserved mutation slightly

        # Determine the point up to which the best car successfully navigated
        # This is the length of its gene that was actually executed before it became inactive
        # If the best car completed its gene, then the collision_point is the full gene length
        collision_point = best_car.current_gene_index
        if not best_car.is_active and best_car.has_collided_with_wall: # If car collided with wall
            pass # collision_point is already set to current_gene_index
        elif not best_car.is_active and not best_car.has_collided_with_wall: # If car became inactive due to gene running out
            collision_point = len(best_car.gene)
            # If the best car ran out of gene, increase gene_length for next generation
            gene_length = min(gene_length + 1000, 100000) # Increase gene length, with a cap
        elif best_car.is_active: # If car is still active (shouldn't happen if simulation ended)
            collision_point = len(best_car.gene)

        # Elitism: Carry over the best car without mutation
        # Truncate the best car's gene to its effective length
        effective_gene = list(best_car.gene[:collision_point])
        new_cars.append(Car(track.center_points[0][0], track.center_points[0][1], angle=start_angle, color=CAR_COLORS[0], gene=effective_gene))
        new_cars[0].reset(track.center_points[0][0], track.center_points[0][1], start_angle) # Reset car state

        # Mutation rate step for later cars
        mutation_rate_step = (max_mutation_rate - dynamic_mutation_rate) / (NUM_CARS - 1) # Distribute remaining mutation range

        for i in range(1, NUM_CARS): # Start from 1 for the rest of the cars
            new_gene = list(effective_gene) # Copy the effective gene
            
            # Calculate car-specific mutation rate
            car_specific_mutation_rate = dynamic_mutation_rate + (i * mutation_rate_step)
            if car_specific_mutation_rate > max_mutation_rate:
                car_specific_mutation_rate = max_mutation_rate

            # Extend the gene with random actions if it's shorter than the initial gene length
            # This ensures new cars have enough actions to potentially go further
            while len(new_gene) < gene_length:
                new_gene.append((random.choice([True, False]),
                                 random.choice([True, False]),
                                 random.choice([True, False]),
                                 random.choice([True, False])))

            for j in range(len(new_gene)):
                current_mutation_rate = car_specific_mutation_rate
                if j < collision_point: # Protect the successful part of the gene
                    current_mutation_rate = mutation_rate_preserved

                if random.random() < current_mutation_rate:
                    new_gene[j] = (random.choice([True, False]),
                                   random.choice([True, False]),
                                   random.choice([True, False]),
                                   random.choice([True, False]))
            new_cars.append(Car(track.center_points[0][0], track.center_points[0][1], angle=start_angle, color=CAR_COLORS[i % len(CAR_COLORS)], gene=new_gene))
            new_cars[i].reset(track.center_points[0][0], track.center_points[0][1], start_angle) # Reset car state
    else:
        # Initial generation: create cars with random genes
        gene_length = 1000 # Define gene_length for initial generation
        for i in range(NUM_CARS):
            new_cars.append(Car(track.center_points[0][0], track.center_points[0][1], angle=start_angle, color=CAR_COLORS[i % len(CAR_COLORS)]))
            new_cars[i].gene = [] # Clear existing gene if any
            for _ in range(gene_length):
                accelerate = random.choice([True, False])
                decelerate = random.choice([True, False])
                turn_left = random.choice([True, False])
                turn_right = random.choice([True, False])
                new_cars[i].gene.append((accelerate, decelerate, turn_left, turn_right))
            
            # Ensure initial forward movement for the first action
            new_cars[i].gene[0] = (True, False, False, False)
    return new_cars

cars = reset_cars() # Initialize the first generation
gene_length = 5000 # Define gene_length globally
simulation_steps = 0
MAX_SIMULATION_STEPS = 999999999 # Effectively no limit
generation_number = 1 # Initialize generation number
last_best_score = -1 # Track the best score from previous generations
generations_since_last_improvement = 0 # Track generations without score improvement

# Game loop
running = True
while running:
    # Event handling (only for quitting the game)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                cars = reset_cars(cars)
                simulation_steps = 0 # Reset simulation steps for new generation
                generation_number += 1 # Increment generation number

    # Update all cars
    screen.fill(BLACK) # Clear screen once per frame
    track.draw(screen) # Draw track once per frame

    all_cars_finished = True
    for i, car in enumerate(cars):
        if car.is_active: # Only update active cars
            # print(f"Main: Updating Car {i+1}") # Removed for performance
            if car.current_gene_index < len(car.gene): # Only update if car still has actions in its gene
                accelerate, decelerate, turn_left, turn_right = car.decide_actions(track)
                # print(f"Main: Car {i+1} actions: Accel={accelerate}, Decel={decelerate}, TurnL={turn_left}, TurnR={turn_right}") # Removed for performance
                car.update(SCREEN_WIDTH, SCREEN_HEIGHT, track, accelerate, decelerate, turn_left, turn_right)
            else:
                car.is_active = False # Car becomes inactive if gene runs out
            all_cars_finished = False
        car.draw(screen)

        # Display score for each car (for debugging/visualization)
        font = pygame.font.Font(None, 24) # Smaller font for multiple scores
        text = font.render(f"Score: {car.score}", True, (255, 255, 255))
        text_rect = text.get_rect(topleft=(30, 10 + i * 20))
        screen.blit(text, text_rect)

        # Draw color box next to score
        color_box_size = 15
        color_box_rect = pygame.Rect(10, text_rect.centery - color_box_size // 2, color_box_size, color_box_size)
        pygame.draw.rect(screen, car.image.get_at((0,0)), color_box_rect)

    # Display generation number
    gen_font = pygame.font.Font(None, 30)
    gen_text = gen_font.render(f"Generation: {generation_number}", True, (255, 255, 255))
    screen.blit(gen_text, (SCREEN_WIDTH - gen_text.get_width() - 10, 10))
    
    if all(not car.is_active or car.has_collided_with_wall for car in cars) or simulation_steps >= MAX_SIMULATION_STEPS:
        cars = reset_cars(cars)
        simulation_steps = 0
        generation_number += 1 # Increment generation number

    simulation_steps += 1

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(1000) # Increased frame rate for faster simulation

# Quit Pygame
pygame.quit()