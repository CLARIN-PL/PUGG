Due to problematic dependencies of `pygaggle`, the `rerank.py` script can be run using separate environment.
To create a new environment defined in `reranker/environment.yml`. Configuration is provided for `conda` package manager.

For reproduction, you don't need to create a new environment manually. 
We integrated the environment creation in `dvc` pipeline using docker.