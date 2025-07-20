# Turbo Racing

![Game Screenshot](screenshot.png)

A fast-paced 2D car racing game built with Python and Pygame. Dodge traffic, score points, and beat your high score in this exciting arcade-style racing game.

## Features

- 🚗 Smooth car controls with realistic physics
- 🛣️ Dynamic road with perspective rendering
- 🚦 Randomly generated enemy cars
- 💥 Collision detection and particle effects
- 🏆 High score system
- 🎮 Multiple game states (Menu, Playing, Game Over)
- ⏯️ Pause functionality

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:
   ```
   pip install pygame
   ```

## How to Play

1. Run the game:
   ```
   python app.py
   ```

2. Controls:
   - **Arrow Keys**: Move your car
   - **P**: Pause/Resume game
   - **ESC**: Quit to menu
   - **SPACE**: Start game/Restart after game over

## Game Rules

- Avoid colliding with other cars
- Score points by staying alive longer
- Beat your high score
- The game gets progressively harder as you play

## Technical Details

- Built with Pygame 2.6.1
- Uses double buffering and hardware acceleration for smooth gameplay
- Implements perspective rendering for a 3D-like effect
- Features optimized rendering for better performance

## Customization

You can easily customize the game by modifying these variables in `app.py`:

- `car_speed`: Adjust the player's car speed
- `enemy_car_speed`: Change the speed of enemy cars
- `enemy_spawn_rate`: Control how often enemy cars appear
- `colors`: Customize the game's color scheme

## Troubleshooting

If you encounter any issues:
1. Make sure all dependencies are installed
2. Check that you're using a compatible Python version
3. Ensure your display supports the required resolution (800x650)

## License

This project is open source and available under the [MIT License](LICENSE).

## Credits

- Developed by Ganesh Ram
- Built with Python and Pygame
- Sound effects and graphics created specifically for this game
