from ml.src.synthetic.graph_generator import generate_graph, generate_dataset
from ml.src.synthetic.nbc_rules import validate_layout

def test_valid_graph_structure():
    g = generate_graph(n_zones=8, valid=True)
    assert g.x.shape[1] == 18
    assert g.edge_index.shape[0] == 2
    assert g.edge_attr.shape[1] == 4

def test_invalid_graph_has_violations():
    g = generate_graph(n_zones=8, valid=False)
    # At least one edge should have label 0 (NBC violation)
    assert (g.y == 0).any()

def test_dataset_balance():
    ds = generate_dataset(n=100)
    valid_count   = sum(1 for d in ds if (d.y > 0).all())
    invalid_count = len(ds) - valid_count
    assert invalid_count > 0, "Should have some invalid layouts"
    assert valid_count > invalid_count, "Should have more valid than invalid"
