"""
hydra_rsvp.py
HYDRA–RSVP Integrator
Defines the HYDRA architecture used in Reflexive Field Dynamics for coupling
personalization (PERSCEN), relevance activation (RAT), and causal memory (CoM)
with RSVP field states (Phi, v, S).
"""

import numpy as np

class HYDRA:
    def __init__(self, N, dx):
        self.N = N
        self.dx = dx
        self.CoM_trajectories = []        # Chain of Memory
        self.RAT_salience = np.ones(N)    # Relevance Activation
        self.PERSCEN_basis = self.initialize_perscen()
        self.memory_decay = 0.95
        self.salience_smoothing = 0.1
        self.integration_strength = 0.8

    def initialize_perscen(self):
        x = np.linspace(0, 2 * np.pi, self.N, endpoint=False)
        basis = []
        for freq in [1, 2, 3, 4]:
            basis.append(np.sin(freq * x))
            basis.append(np.cos(freq * x))
        return np.array(basis)

    def update_RAT(self, Phi, v, S):
        entropy_grad = np.gradient(S, self.dx)
        field_coherence = Phi * S
        new_salience = (np.abs(entropy_grad)
                        + np.abs(field_coherence)
                        + 0.1 * np.random.randn(self.N))
        self.RAT_salience = (
            self.salience_smoothing * new_salience
            + (1 - self.salience_smoothing) * self.RAT_salience
        )
        return self.RAT_salience

    def update_CoM(self, Phi, v, S):
        state_vector = np.stack([Phi, v, S])
        if len(self.CoM_trajectories) > 100:
            self.CoM_trajectories.pop(0)
        self.CoM_trajectories.append(state_vector.copy())
        if len(self.CoM_trajectories) > 1:
            for i in range(len(self.CoM_trajectories) - 1):
                self.CoM_trajectories[i] *= self.memory_decay

    def retrieve_CoM_pattern(self, current_state):
        if not self.CoM_trajectories:
            return np.zeros_like(current_state[0])
        memories = np.array(self.CoM_trajectories)
        current_expanded = current_state[:, np.newaxis, :]
        similarities = np.exp(-np.sum((memories - current_expanded) ** 2, axis=(0, 2)))
        most_similar_idx = np.argmax(similarities)
        return memories[most_similar_idx, 0, :]

    def integrate_HYDRA(self, Phi, v, S):
        salience = self.update_RAT(Phi, v, S)
        self.update_CoM(Phi, v, S)
        memory_pattern = self.retrieve_CoM_pattern(np.stack([Phi, v, S]))
        perscen_weights = self.PERSCEN_basis @ salience
        perscen_target = np.zeros_like(Phi)
        for i, weight in enumerate(perscen_weights):
            if i < len(self.PERSCEN_basis):
                perscen_target += weight * self.PERSCEN_basis[i]
        memory_component = 0.3 * memory_pattern
        salience_component = 0.4 * salience * np.sin(Phi)
        perscen_component = 0.3 * perscen_target
        Psi_star = memory_component + salience_component + perscen_component
        Psi_star /= np.max(np.abs(Psi_star)) + 1e-8
        return Psi_star

