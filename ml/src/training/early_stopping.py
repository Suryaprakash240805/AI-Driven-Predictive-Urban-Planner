class EarlyStopping:
    def __init__(self, patience: int = 15, delta: float = 1e-4):
        self.patience = patience; self.delta = delta
        self.counter  = 0; self.best_score = None; self.should_stop = False

    def step(self, val_loss: float) -> bool:
        if self.best_score is None or val_loss < self.best_score - self.delta:
            self.best_score = val_loss; self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
        return self.should_stop
