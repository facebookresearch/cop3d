# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


import os

from co3d.dataset.download_dataset_impl import build_arg_parser, download_dataset


REPO_ROOT = __file__.rsplit(os.sep, 2)[0]
DEFAULT_LINK_LIST_FILE = os.path.join(REPO_ROOT, "links", "links.json")
DEFAULT_SHA256S_FILE = os.path.join(REPO_ROOT, "links", "cop3d_sha256.json")


if __name__ == "__main__":
    parser = build_arg_parser("COP3D", DEFAULT_LINK_LIST_FILE, DEFAULT_SHA256S_FILE)
    args = parser.parse_args()
    download_dataset(
        str(args.link_list_file),
        str(args.download_folder),
        n_download_workers=int(args.n_download_workers),
        n_extract_workers=int(args.n_extract_workers),
        download_categories=args.download_categories,
        checksum_check=bool(args.checksum_check),
        single_sequence_subset=False,
        clear_archives_after_unpacking=bool(args.clear_archives_after_unpacking),
        sha256s_file=str(args.sha256_file),
        skip_downloaded_archives=not bool(args.redownload_existing_archives),
    )
