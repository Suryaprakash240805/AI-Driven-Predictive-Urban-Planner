import yaml, torch
from ml.src.synthetic.graph_generator import generate_dataset
from ml.src.synthetic.augmentor import augment_dataset
from ml.src.data_pipeline.dataset_splitter import split_dataset
from ml.src.data_pipeline.feature_normalizer import NodeFeatureNormalizer
from ml.src.training.trainer import train
from ml.src.evaluation.evaluator import evaluate

def main():
    with open("ml/configs/model_config.yaml") as f:
        cfg = yaml.safe_load(f)

    model_cfg = cfg["model"]
    train_cfg = {**cfg["train"], **model_cfg}

    print("="*55)
    print("  URBAN PLANNER – GNN TRAINING PIPELINE")
    print("="*55)

    print("\n[1/5] Generating synthetic dataset...")
    raw = generate_dataset(n=cfg["train"]["batch_size"] * 500, use_type="residential")

    print("[2/5] Augmenting dataset...")
    augmented = augment_dataset(raw, factor=2)

    print("[3/5] Splitting dataset...")
    train_ds, val_ds, test_ds = split_dataset(augmented)

    print("[4/5] Normalizing features...")
    norm = NodeFeatureNormalizer()
    norm.fit(train_ds)
    train_ds = norm.transform(train_ds)
    val_ds   = norm.transform(val_ds)
    test_ds  = norm.transform(test_ds)
    norm.save("ml/checkpoints/scaler.pkl")

    print(f"  Train: {len(train_ds)} | Val: {len(val_ds)} | Test: {len(test_ds)}")

    print("[5/5] Training GNN model...")
    model = train(train_ds, val_ds, train_cfg)

    print("\n[EVAL] Evaluating on test set...")
    model.load_state_dict(torch.load("ml/checkpoints/best_model.pt"))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results = evaluate(model.to(device), test_ds, device)
    print("\nFinal Test Metrics:", results)

if __name__ == "__main__":
    main()
