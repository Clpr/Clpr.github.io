Refactor the project consisting of two python modules: `fwcp_bunch_and_symmetric.py` and `fwcp_hw2009.py` into a single-file python module named `fwcp.py`. The new module file should be saved in the current project folder.

Requirements

0. Materials for your job have been placed in the current folder,while you are allowed to search the internet to get what you need. The environment for development is a Conda environment `PyMain`. You can activate it in the terminal using `conda activate PyMain`. You have the permission to install packages if needed.
1. Understand the context, math formulas, and programs in the two original python files and `index.md` in the folder. Make sure your `fwcp.py` can generate the same results as the original two python modules.
2. The new `fwcp.py` should have consistent API with each other and detailed docstring with usage examples. The programming style should be OOP.
3. Optimize the programs if needed, but do make sure correctness.
4. After creating `fwcp.py`, write a Jupyter notebook `demo.ipynb` to illustrate usage examples. The demo should show the usage of all different types of FWCP estimators, and create visualization figures such as actual distribution vs. counterfactual PDF using different methods.
5. After creating `fwcp.py`, write a single `test.py` file for tests.