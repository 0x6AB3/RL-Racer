# Racer - A Genetic Algorithm Project

A genetic algorithm trains multiple cars to navigate a 2D racing track built with Pygame.

## How It Works

This project uses a genetic algorithm to teach a population of cars how to drive around a pre-defined track.

*   **Genes**: Each car has a "gene," which is a pre-determined sequence of actions (accelerate, decelerate, turn left, turn right).
*   **Fitness Function**: The fitness of each car is evaluated based on how many gates it successfully passes. The time taken and distance traveled are used as tie-breakers.
*   **Evolution**: After all cars have either crashed or run out of "genes," a new generation is created.
    *   **Elitism**: The best-performing car from the previous generation, always represented by the **red car**, is preserved. Its successful gene sequence is directly carried over to the next generation, ensuring that the best traits are never lost.
    *   **Crossover & Mutation**: The rest of the new generation is created by taking the successful gene sequence from the best car and mutating it with varying intensity. Cars with more aggressive mutations are encouraged to explore new strategies, while those with less mutation will behave more similarly to the previous best car.

Over many generations, the cars evolve to navigate the track more effectively.

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Racer
    ```

2.  **Install dependencies:**
    This project requires Pygame.
    ```bash
    pip install pygame
    ```

3.  **Run the simulation:**
    ```bash
    python main.py
    ```

## Controls

- The simulation runs automatically.
- **SPACE**: Press the spacebar to end the current generation and start the next one immediately.
- **Close Window**: Quit the simulation.

## Code Structure

- `main.py`: Contains the main game loop, handles the genetic algorithm's generational logic, and manages the overall simulation.
- `Car.py`: Defines the `Car` class, including its physics, movement, collision detection, and the logic for interpreting its genetic code.
- `Track.py`: Defines the `Track` class, responsible for generating the track's geometry, including the boundaries and the gates.
