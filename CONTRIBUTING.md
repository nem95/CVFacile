# Contributing to CVfacile

Thanks for helping! Before opening a pull request:

1. **Read and accept the [CLA](CLA.md)** by adding this sentence to the description of your first pull request:
   > I have read the CVfacile CLA and I agree to its terms for my contributions.

   The CLA is needed because CVfacile is also offered under a commercial license: without it, your code could not be shipped under both licenses.
2. Keep the Python standard library as the only required dependency (Python 3.8+).
3. Run the tests: `python3 -m unittest discover -s tests`.
4. If you add or change a template, rebuild the renders (`python3 scripts/render_examples.py`) and commit `examples/output/`. Check that a long, real-world CV still fits on one page.
5. Never put real personal data in examples or tests.

Ideas welcome: new templates, new languages (`LABELS` in templates), import from JSON Resume or LinkedIn.
