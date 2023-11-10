# Reinforcement Learning and Path Planning for 2D Grid World

This repository contains Python implementations of various reinforcement learning algorithms, including Value-Iteration and Q-Learning, applied to a 2D grid world Markov Decision Process (MDP) reminiscent of a Pac-Man game. Additionally, the repository includes the Mini-Max algorithm and common path-planning techniques such as A*, Dijkstra, and bidirectional search.

## Directory Structure

### Markov Decision Process
The `Markov Decision Process` directory (`Markov Decision Process/src/python_client`) includes code for a 2D grid world Markov Decision Process with Value Iteration implementation.

### Mini-Max
The `Mini-Max` directory (`Mini-Max/src/python_client`) encompasses the Python implementation of the Mini-Max algorithm. Mini-Max is a decision-making algorithm commonly used in two-player games, aiming to minimize the possible loss for a worst-case scenario.

### Path Planning
The `Path-Planning` directory (`Path Planning/src/python_client`) houses Python implementations of common path-planning techniques. This includes A*, Dijkstra, and bidirectional search algorithms designed to find the optimal paths in the grid world.

## Requirements
Make sure to install the required Python packages using the following command:
```
pip install -r requirements.txt
```
The following packages are necessary for running the code:

```
cssselect2==0.4.1
lxml==4.6.3
Pillow==8.3.2
pygame==2.0.1
reportlab==3.6.1
svg.path==4.1
svglib==1.1.0
tinycss2==1.1.0
webencodings==0.5.1
matplotlib==3.6.2
numpy==1.23.5
pandas==1.5.2
```

Feel free to explore the different directories and leverage the provided implementations for reinforcement learning and path planning in a 2D grid world MDP. If you encounter any issues or have suggestions for improvement, please open an issue or submit a pull request.
