# Licence evidence and remaining review

Evidence date: 13 November 2026. dependencies.resolved.json retains the initial installed Python 3.12 inventory from Actions run 43337947734. licences.wheels.c1f9ad7.json and wheels.c1f9ad7.json contain the later actual 63-wheel notice/hash inventory from run 43347812566, whose fresh offline installation and model lifecycle passed. These establish observed artifacts and declared terms, not blanket legal clearance.

- Soup 0.77.2 was built from af2f5d5000f7baec6386a72a6d16e82383eb5303. The observed wheel SHA-256 was e7285d5077da078c5e1fed5de8617d2feec4055c340c657793e2cd48d4319042. This identifies that build, not all future wheel builds.
- Exact upstream Apache-2.0 LICENSE and NOTICE are retained under third_party/. No upstream source changes were made.
- Model HuggingFaceTB/SmolLM2-135M-Instruct revision 12fd25f77366fa6b3b4b768ec3050bf629380bac declares Apache-2.0. Provisioning verifies that metadata and preserves its model card. It does not download the upstream training_args.bin or unrelated ONNX exports.
- AIRON's integration code uses the repository's MIT licence. The original copyright notice remains in the repository root.
- Synthetic training/test fixtures have an explicit CC0-1.0 declaration.
- AIP remains proprietary in the inspected source; no AIP source or binary is redistributed here.

## Resolved Python inventory

63 distributions were present, including test/build tools. Full names, versions, licence metadata and declared licence-file names appear in dependencies.resolved.json. Operating-system packages and transitive native libraries are not exhaustively inventoried there.

The initial metadata-only report contained blank selected licence fields. Inspecting the actual wheels found packaged notices for Jinja2 (1), markdown-it-py (2), mdurl (1), safetensors (1) and setuptools including vendored components (24). Soup includes 6 matched licence/notice files. Counts describe filename-based notice inventory, not separate legal opinions.

The c1f9ad7 wheel inventory exposed two missing packaged-notice sets: AIRON and tokenizers. AIRON now includes its unchanged root MIT LICENSE through the package's license-files declaration. Preparation supplements tokenizers 0.23.3 with the exact Apache-2.0 LICENSE from upstream commit 301277072263fb3830eb66eec7e47adadf76f1dc, resolved from its annotated v0.23.3 tag. The copy is in third_party/tokenizers-LICENSE.txt; preparation records its digest and source revision. This does not imply that every native transitive component shares that licence. Current packaging execution status belongs to STATUS.md and the latest wheel inventory.

Metadata also includes compound terms, including numpy's bundled licences, tqdm's MPL-2.0 AND MIT, and regex's Apache-2.0 AND CNRI-Python. Retain the actual licence/notice files and review redistribution conditions for the exact wheels and native libraries. Do not flatten these entries to a single permissive licence label.

The branch redistributes AIRON source and attribution files, not a complete model/runtime image. Before distributing a runtime, review the exact generated wheel/notices set, independently approved hashes, model terms and native platform dependencies. The testbed's Ubuntu/Python/bubblewrap/util-linux/strace installation is a preparation prerequisite; the Python wheel inventory is not an OS SBOM. An open-source code licence does not grant rights to arbitrary third-party weights or data.
