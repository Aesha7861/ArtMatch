# ArtMatch

**Team RB — Aesha Gadhiya · Lizi Maisuradze**  

## Overview

ArtMatch is an artwork-to-artwork retrieval prototype for the CU campus collection. Given an artwork image, it retrieves five related artworks from a gallery of 189 images across four floors, displaying artwork IDs, floor locations, similarity scores and estimated visual attributes.

## Approach and results

- **Baseline:** Pretrained, frozen CLIP ViT-B/32 extracts 512-dimensional image embeddings for cosine-similarity retrieval.
- **Adaptation:** A 512 → 256 → 256 projection head is trained using supervised contrastive learning on five WikiArt styles (2,500 training and 500 artist-disjoint validation images).
- **Evaluation:** WikiArt same-style validation Precision@5 improved from **0.7264** (original CLIP) to **0.7456** (adapted CLIP). The best checkpoint was at epoch 2; longer training showed overfitting.
- **Attribute descriptions:** A separate combination of frozen CLIP image–text comparisons and pixel-based color analysis; predictions are estimates.

## Submission files

| File | Purpose |
|---|---|
| `artmatch_baseline.ipynb` | CU gallery preprocessing, frozen CLIP embeddings, baseline retrieval and attribute analysis. |
| `artmatch_training.ipynb` | WikiArt preparation and split checks, feature extraction, projection-head training, evaluation and adapted retrieval. |
| `artmatch_gallery_ui.py` | Browser interface for artwork upload and top-five results. |
| `gallery_metadata.csv` | CU artwork IDs, image filenames and floor information. |
| `cu_clip_baseline.npz` | Cached CLIP embeddings for the CU gallery. |
| `wikiart_style_splits.csv` | WikiArt training/validation assignments, if included. |
| `wikiart_clip_features.npz` | Cached WikiArt image embeddings, if included. |
| `requirements.txt` | Python dependencies. |
| `ArtMatch_File_and_Experiments_Description.pdf` | Dataset, source-file and experiment documentation, if included. |
| `Team_RB_Gadhiya_Maisuradze.pdf` | Final presentation. |

The professor's submission structure uses **`Data/`**, **`Sources/Experiment_1…N/`** and **`Presentation/`**. File paths within those folders depend on the final archive arrangement.

## Running the application

Install dependencies with `python -m pip install -r requirements.txt`. Set `PROJECT_ROOT` and the gallery paths in the notebooks to the local project location. Run the adapted model-loading, gallery-retrieval, attribute-analysis and UI-launcher sections of `artmatch_training.ipynb` in order. The interface uses port `8765` in the original JupyterHub environment.

**Required for a working demo:** CU artwork images, gallery metadata, embeddings and the matching trained projection-head checkpoint. These may need to be supplied separately if excluded from the archive.

**Scope:** WikiArt Precision@5 evaluates same-style retrieval, not human-rated CU relevance. No independent WikiArt test split was created, and artwork attributes may be inaccurate.
