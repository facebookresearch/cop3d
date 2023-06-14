<center>
<img src="./assets/cop3d-logo.png" width="512" />
</center>
<br>

# COP3D: Common Pets in 3D

**[[project]](https://cop3d.github.io/)** | **[[paper]](https://arxiv.org/abs/2211.03889)**

COP3D is a dataset of 4,200 distinct pet videos.
This repository contains download scripts, examples of usage, and format description.

## Download

The compressed dataset takes **322 GB of space**. We distribure it in 20 GB chunks.
The links to all dataset files are present in this repository in [links/links.json](links/links.json).
We provide an automated way of downloading and decompressing the data.

First, run the install script that will take care of dependencies:

```
pip install -e .
```

Then run the script (make sure to change `<DESTINATION_FOLDER>`):

```
python ./cop3d/download_dataset.py --download_folder <DESTINATION_FOLDER> --checksum_check
```

The script has multiple parameters, e.g. `--download_categories cat` will limit the download to `cat` category,
and `--clear_archives_after_unpacking` flag will remove the redundant archives.
Run `python ./cop3d/download_dataset.py -h` for the full list of options.


## API Quick Start and Tutorials

Make sure the setup is done and the dataset is downloaded as per above.

There are multiple ways to access the dataset. We recommend using PyTorch3D data loaders.
In particular, the example below uses `SqlIndexDataset` class available in PyTorch3D v0.7.4 or newer.
As a basic example, the following code creates a dataset object with filters on category and subset (in this case, training set of dogs for the manyview protocol):

```python
SUBSET_NAME = "manyview"  # OR "fewview_dev" OR "fewview_train"
METADATA_FILE = os.path.join(DATASET_ROOT, "metadata.sqlite")
SUBSET_LISTS_FILE = os.path.join(DATASET_ROOT, f"set_lists/set_lists_{SUBSET_NAME}.sqlite")

dataset_dog_train = SqlIndexDataset(
    sqlite_metadata_file=METADATA_FILE,
    dataset_root=DATASET_ROOT,  # root for loading images
    subset_lists_file=SUBSET_LISTS_FILE,
    subsets=["train"],
    pick_categories=["dog"],
)
dataset_dog_train.frame_data_builder.load_depths = False  # the dataset does not provide depth maps
```

This object can be indexed using either global integer indices or (sequence_name, frame_id) pairs to get individual frame data.
It contains image tensor in `image_rgb` field, e.g. `dataset_dog_train["1010_4208_3256", 193].image_rgb`,
and PyTorch3D camera object in `camera` field, e.g. `dataset_dog_train["1010_4208_3256", 193].camera`.

For more information on this API, including data loader classes that can be plugged in to the training loop directly, see the tutorial in [examples/high_level_api.ipynb](examples/high_level_api.ipynb).

For the usage outside PyTorch, see [low-level API tutorial](examples/low_level_api.ipynb) and format description below.

## Dataset Format

While we recommend using the high-level API (see above), we also provide a brief description of the underlying format here. Here is the directory layout on disk:

```
DATASET_ROOT
    ├── cat
    │   ├── <sequence_name_0>
    │   │   ├── images
    │   │   ├── masks
    │   │   └── pointcloud.ply
    │   ├── <sequence_name_1>
    │   │   ├── images
    │   │   ├── masks
    │   │   └── pointcloud.ply
    │   ├── ...
    │   ├── <sequence_name_N>
    │   ├── set_lists
    │   │   ├── set_lists_fewview_train.json
    │   │   ├── set_lists_fewview_dev.json
    │   │   ├── set_lists_manyview_0.json
    │   │   ├── ...
    │   │   ├── set_lists_manyview_47.json
    │   ├── eval_batches
    │   │   ├── eval_batches_fewview_train.json
    │   │   ├── eval_batches_fewview_dev.json
    │   │   ├── eval_batches_manyview_0.json
    │   │   ├── ...
    │   │   ├── eval_batches_manyview_47.json
    │   ├── frame_annotations.jgz
    │   ├── sequence_annotations.jgz
    ├── dog
    │   ├── ...
    ├── metadata.sqlite
    ├── set_lists
    │   ├── set_lists_manyview.sqlite
    │   ├── set_lists_fewview_train.sqlite
    │   ├── set_lists_fewview_dev.sqlite
    ├── eval_batches
    │   ├── eval_batches_manyview.json
    │   ├── eval_batches_fewview_train.json
    │   ├── eval_batches_fewview_dev.json
```

There are currently two categories: `cat` and `dog`.
Metadata are duplicated in two formats: SQL and JSON, which are used by PyTorch3D’s `SqlIndexDataset` and `JsonIndexDataset` classes, respectively.
The former is preferable, as it provides a richer API and shorter warm-up time, however the JSON format has an advantage of being human-readable.

### SQL format
Metadata are stored in `DATASET_ROOT` merged for all categories.
In particular, it facilitates training category-agnostic models.
The main index is stored in `metadata.sqlite` file, containing `frame_annots` and `sequence_annots` tables that can be joined on `sequence_name` key.
Frame annotations contain, in particular, image and mask paths and camera parameters (the latter are stored as blobs).

The training splits of frames (train/val/test) are stored in `DATASET_ROOT/set_lists`.
We store them separately from the main metadata in order to enable users to define custom splits.
In particular, `set_lists_manyview.sqlite` contains the splits for the many-view (“overfit to a scene”) protocol.
In practice, these set lists should be used with the `pick_sequence` filter.
The file `set_lists_fewview_dev.sqlite` contains the splits for the few-view (“generalise to a new scene”) protocol.
The sequences between train and val/test sets do not overlap.
The file `set_lists_fewview_train.sqlite` is the same protocol allowing generalisation across instances but val/test frames are held out from the training sequences.

The JSON files in `DATASET_ROOT/eval_batches` define the evaluation batches used in the paper.
Each file corresponds to a set_lists file, and the target frame in each batch (the first or the only) is always taken from the test split of the corresponding protocol.
The batches can contain more than one frame since few-view models are expected to be conditioned on known frames.
Note again that for many-view experiments, these files need to be filtered by sequence.

### Legacy JSON (CO3Dv2) format
This is an equivalent format, where metadata are partitioned by category, and in case of many-view set lists, by sequence.
The main metadata are stored in zipped json files at `DATASET_ROOT/<category>/frame_annotations.jgz` and `DATASET_ROOT/<category>/sequence_annotations.jgz`, which correspond to the slices of the corresponding tables of `metadata.sqlite`.

The training splits are stored in JSON format in `DATASET_ROOT/<category>/set_lists`, and eval batches are stored in `DATASET_ROOT/<category>/eval_batches`. Besides the format, they are equivalent to the global counterparts described above, split by category.
Many-view set lists and eval batches are split by sequence, i.e. there is a separate JSON file for each sequence, so the dataset class does not need to additionally filter by sequence.

For more information on this format, see [CO3D documentation](https://github.com/facebookresearch/co3d/blob/main/README.md#dataset-format).


## Reference
If you use our dataset, please cite the paper:
```
@article{sinha2023common,
  title={Common Pets in 3D: Dynamic New-View Synthesis of Real-Life Deformable Categories},
  author={Sinha, Samarth and Shapovalov, Roman and Reizenstein, Jeremy and Rocco, Ignacio and Neverova, Natalia and Vedaldi, Andrea and Novotny, David},
  journal={CVPR},
  year={2023}
}
```

## License

The data are released under the [CC BY-NC 4.0 license](LICENSE).

