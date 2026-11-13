# Keep the original model usable after training cancellation

Review of Controller._execute found that the process-start callback applied a cancelled training job's state to every later worker operation using that job's approved model/dataset. After cancelling training, infer could therefore launch a baseline worker and immediately stop it. This did not activate an unapproved candidate, but it made cancellation disrupt the original model.

The regression was reproduced locally before the fix: test_cancelled_training_does_not_cancel_later_baseline_inference failed because sandbox.stop was called; the adjacent cancelled-launch race test passed. The callback now applies that cancellation race check only when operation == train. A cancelled job still cannot restart or register a checkpoint, and a process launched after cancellation is still stopped.

The real fault harness now cancels after actual optimizer progress, verifies that the process stopped and candidate registration remains denied, then performs real baseline inference over the complete frozen evaluation set while confirming the job remains CANCELLED. It subsequently exercises the actual malformed safetensors parser. The fixture tests are not counted as proof that these real operations pass; the new Actions result must supply that evidence.

This change leaves the pinned model, authorized dataset/rehearsal, learning configuration, frozen evaluation and deployment gate unchanged. STATUS.md and LEDGER.md record the final executed result, including any failure.
