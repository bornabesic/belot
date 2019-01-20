import torch
import torch.nn as nn

class PolicyGradientLoss(nn.Module):

    def forward(self, log_action_probabilities, discounted_rewards):
        # log_action_probabilities -> (B, timesteps, 1)
        # discounted_rewards -> (B, timesteps, 1)

        losses = - discounted_rewards * log_action_probabilities # -> (B, timesteps, 1)
        loss = losses.mean()
        return loss
