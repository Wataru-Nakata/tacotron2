from text import symbols
import yaml



def create_hparams(hparams_string=None, verbose=False):
    """Create model hyperparameters. Parse nondefault from given string."""
    with open('config.yaml') as f:
        hparams = yaml.safe_load(f)

    return hparams
