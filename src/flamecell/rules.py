"""
Forest Fire Simulation Framework

This module provides rule functions for the grid update.
"""

import numpy as np

# Rules
# ignite under certain probability, humidity and wind
def ignite(x, y, state, health, neighbors, 
           prob=0.15, humidity=40, wind=np.array([0,0]), temp=20, **kwargs):
    """
    Determine if a cell should ignite based on neighbors, humidity, wind, and temperature.

    Parameters
    ----------
    x, y: int
        X, Y-coordinate of the cell.
    state : str
        Current state of the cell.
    health : int
        Health value of the cell.
    neighbors : list of tuples
        List of (neighbor_state, dx, dy) for neighboring cells.
    prob : float, optional
        Base ignition probability (default is 0.15).
    humidity : float, optional
        Humidity percentage (default is 40).
    wind : np.ndarray, optional
        Wind vector (default is [0, 0]).
    temp : float, optional
        Temperature in degrees Celsius (default is 20).

    Returns
    -------
    tuple
        New state and health of the cell.
    """
    if state in ["TREE", "GRASS"]:
        ignition_prob = 0.0
        for neighbor_state, dx, dy in neighbors:
            if neighbor_state == "FIRE":
                ignition_prob += 1 + (dx * wind[0] + dy * wind[1]) * 0.02     
        if np.random.rand() < ignition_prob * prob * (1 - 0.01 * humidity) * (1 + 0.02 * (temp - 20)):
            return "FIRE", health  # Start burning
    return state, health

# https://www.sciencedirect.com/science/article/pii/S2666449624000422#:~:text=This%20study%20employs%20cellular%20automata%20principles%20to%20analyze,a%20multifactor%20coupled%20forest%20fire%20model%20is%20developed.
# p_burn = p0 * Ks * Kw * Ktheta
# take Ks = 1 (Pine)
# this model produce weird result in my case
def ignite1(x, y, state, health, neighbors, 
            prob=0.15, humidity=40, wind=np.array([0,0]), temp=20, wspd=0, **kwargs):
    """
    Alternative ignition rule based on multifactor fire model.
    Based on the model: p_burn = p0 * Ks * Kw * Ktheta
    not working well now.

    Parameters
    ----------
    x, y: int
        X, Y-coordinate of the cell.
    state : str
        Current state of the cell.
    health : int
        Health value of the cell.
    neighbors : list of tuples
        List of (neighbor_state, dx, dy) for neighboring cells.
    prob : float, optional
        Unused base probability (default is 0.15).
    humidity : float, optional
        Humidity percentage (default is 40).
    wind : np.ndarray, optional
        Wind vector (default is [0, 0]).
    temp : float, optional
        Temperature in degrees Celsius (default is 20).
    wspd : float, optional
        Wind speed in m/s (default is 0).

    Returns
    -------
    tuple
        New state and health of the cell.
    """
    if state in ["TREE", "GRASS"]:
        p_burn = 0
        p_wind_corr = 0
        p_count = 0
        for neighbor_state, dx, dy in neighbors:
            if neighbor_state == "FIRE":
                p_wind_corr += 0.1 * (dx * wind[0] + dy * wind[1])
                p_count += 1
        if p_count > 0:
            p_burn = 0.03 * temp + 0.1 * 16.67 * p_wind_corr + 0.01 * (1 - 0.01 * humidity) - 0.3
            return "FIRE", health  # Start burning
    return state, health

def burning(x, y, state, health, neighbors, **kwargs):
    """
    Update cell state if it is burning.

    Parameters
    ----------
    x, y : int
        X, Y-coordinate of the cell.
    state : str
        Current state of the cell.
    health : int
        Health value of the cell.
    neighbors : list of tuples
        Not used.
    **kwargs : dict
        Additional arguments (ignored).

    Returns
    -------
    tuple
        New state and health of the cell.
    """
    if state == "FIRE":
        health -= np.random.randint(1,3)
        if health <= 0:
            return "ASH", 0
    return state, health