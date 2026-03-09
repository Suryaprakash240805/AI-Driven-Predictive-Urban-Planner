import torch
import torch.nn as nn

class UrbanPlannerLoss(nn.Module):
    """
    L_total = α*L_graph + β*L_edge + γ*L_nbc
    """
    def __init__(self, alpha=0.4, beta=0.4, gamma=0.2):
        super().__init__()
        self.alpha = alpha; self.beta = beta; self.gamma = gamma
        self.bce   = nn.BCELoss()

    def forward(self, g_score, e_scores, g_labels, e_labels):
        l_graph = self.bce(g_score.squeeze(), g_labels.float())
        l_edge  = self.bce(e_scores.squeeze(), e_labels.float())
        l_nbc   = (e_labels == 0).float().mean()
        total   = self.alpha*l_graph + self.beta*l_edge + self.gamma*l_nbc
        return total, l_graph, l_edge, l_nbc
