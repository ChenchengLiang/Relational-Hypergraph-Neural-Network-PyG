from torch_geometric.datasets import TUDataset
from torch_geometric.loader import DataLoader
def hyper_GNN_on_standard_dataset():

    dataset = TUDataset(root='/tmp/ENZYMES', name='ENZYMES', use_node_attr=True)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

if __name__ == '__main__':
    hyper_GNN_on_standard_dataset()