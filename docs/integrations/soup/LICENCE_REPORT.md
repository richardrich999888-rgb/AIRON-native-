# Licence evidence and remaining review

Evidence date: 13 November 2026. Resolved metadata came from the actual Python 3.12 environment in GitHub Actions run 43337947734, before the sandbox probe failed. This establishes installed versions and declared metadata, not an executed model or legal clearance.

- Soup 0.77.2 was built from af2f5d5000f7baec6386a72a6d16e82383eb5303. The observed wheel SHA-256 was e7285d5077da078c5e1fed5de8617d2feec4055c340c657793e2cd48d4319042. This identifies that build, not all future wheel builds.
- Exact upstream Apache-2.0 LICENSE and NOTICE are retained under third_party/. No upstream source changes were made.
- Model HuggingFaceTB/SmolLM2-135M-Instruct revision 12fd25f77366fa6b3b4b768ec3050bf629380bac declares Apache-2.0. Provisioning verifies that metadata and preserves its model card. It does not download the upstream training_args.bin or unrelated ONNX exports.
- AIRON's integration code uses the repository's MIT licence. The original copyright notice remains in the repository root.
- Synthetic training/test fixtures have an explicit CC0-1.0 declaration.
- AIP remains proprietary in the inspected source; no AIP source or binary is redistributed here.

## Resolved Python inventory

63 distributions were present, including test/build tools. Full names, versions, licence metadata and declared licence-file names appear in dependencies.resolved.json. Operating-system packages and transitive native libraries are not exhaustively inventoried there.

Packages with blank selected licence metadata: airon-adaptation, Jinja2, markdown-it-py, mdurl, safetensors, setuptools, tokenizers. AIRON now declares MIT in pyproject.toml; the others still require checking their actual packaged licence files. A blank field is an open review item, not an inference that a package is unlicensed.

Metadata also includes compound terms, including numpy's bundled licences, tqdm's MPL-2.0 AND MIT, and regex's Apache-2.0 AND CNRI-Python. Retain the actual licence/notice files and review redistribution conditions for the exact wheels and native libraries. Do not flatten these entries to a single permissive licence label.

The branch redistributes AIRON source and attribution files, not a complete model/runtime bundle. Offline runtime redistribution remains gated on a clean wheelhouse build, full notices, hash verification, model terms and platform dependency review. An open-source code licence does not grant rights to arbitrary third-party weights or data.
