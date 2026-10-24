# Dataset archive handling

The separately supplied corpus archive is approximately 213 MB and includes datasets with potentially different licensing and redistribution conditions. It is intentionally excluded from this source repository.

Recommended workflow:
1. Keep the archive outside the cloned repository or in a separately permissioned storage location.
2. Review the source, edition, license, and redistribution terms for each included dataset.
3. Extract only files permitted for your intended use into `data/raw/` using the layout in [`../data/README.md`](../data/README.md).
4. Keep raw data, derived exports, and vector indexes untracked; the repository's `.gitignore` excludes them.
5. Document dataset versions and checksums in a local manifest for reproducibility.

The source-code ZIP is represented in the repository as organized source files rather than as a nested ZIP artifact.
