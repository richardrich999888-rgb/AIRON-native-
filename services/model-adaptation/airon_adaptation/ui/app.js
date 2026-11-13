let state = {};
const result = document.querySelector('#result');
const message = document.querySelector('#message');
async function call(operation, params = {}) {
  const response = await fetch('/api/operation', {
    method: 'POST', headers: {'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + document.querySelector('#token').value},
    body: JSON.stringify({operation, params})
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || 'Request failed');
  return body;
}
function latest(kind) {
  const values = state[kind] || [];
  if (!values.length) throw new Error('No ' + kind + ' is available. Complete the preceding step.');
  return values.at(-1).id;
}
function renderSummary() {
  const job = state.job?.at(-1), evaluation = state.evaluation?.at(-1), deployment = state.deployment?.at(-1);
  const set = (id, value) => { document.getElementById(id).textContent = value; };
  set('training-state', job?.status || 'No job prepared');
  const measured = job?.result;
  set('training-detail', measured
    ? measured.steps + ' steps · ' + measured.training_seconds.toFixed(1) + ' s · ' + measured.changed_parameters + ' tensors changed'
    : 'Only a completed, measured run can register a candidate.');
  for (const [split, prefix] of [['test', 'routing'], ['regression', 'regression']]) {
    const score = evaluation?.metrics?.[split];
    set(prefix + '-score', score
      ? Math.round(score.baseline_accuracy * score.count) + '/' + score.count + ' → ' +
        Math.round(score.candidate_accuracy * score.count) + '/' + score.count : 'Not evaluated');
    set(prefix + '-detail', score ? score.count + ' frozen questions · ' +
      (evaluation.passed ? 'Combined gate passed' : 'Deployment blocked by evaluation') : 'No measured evaluation in this workspace.');
  }
  set('active-model', deployment ? (deployment.active ? 'Adapted candidate' : 'Original model') : 'Not provisioned');
  set('deployment-detail', deployment ? 'Local deployment version ' + deployment.version : 'Prepare the approved model first.');
  const approval = state.approval?.at(-1);
  const candidate = state.candidate?.find(c => c.id === approval?.candidate_id);
  const reviewed = state.evaluation?.find(e => e.id === approval?.evaluation_id);
  set('review-summary', approval
    ? 'Review: ' + approval.decision + '. Candidate ' + approval.candidate_id +
      '. Evaluation ' + approval.evaluation_id + ' (' + (reviewed?.passed ? 'passed' : 'not passed') +
      '). Candidate digest ' + (candidate?.digest || 'unavailable') + '. Requested by ' + approval.requested_by + '.'
    : 'No deployment request. Evaluate a candidate before requesting review.');
}
async function refresh() { state = await call('status'); renderSummary(); }
async function act(operation) {
  for (const button of document.querySelectorAll('button')) button.disabled = true;
  message.textContent = 'Working locally…';
  try {
    await refresh();
    let params = {};
    if (operation === 'query_knowledge') params = {question: document.getElementById('question').value,
      enabled: ['OPS-001', 'OPS-002', 'FIN-001', 'IT-001']};
    if (operation === 'infer') params = {dataset_id: latest('dataset')};
    if (['start_training','cancel_training','register_checkpoint'].includes(operation))
      params = {job_id: latest('job')};
    if (['evaluate_candidate','export_model'].includes(operation))
      params = {candidate_id: latest('candidate')};
    if (operation === 'request_deployment')
      params = {candidate_id: latest('candidate'), evaluation_id: latest('evaluation')};
    if (operation === 'approve_deployment')
      params = {approval_id: latest('approval'), decision: 'APPROVED'};
    if (operation === 'activate_model') params = {approval_id: latest('approval')};
    if (['approve_deployment','activate_model','rollback_model'].includes(operation) &&
        !window.confirm('Confirm ' + operation.replaceAll('_',' ') + ' for the displayed experiment?')) {
      message.textContent = 'No change made.'; return;
    }
    const response = await call(operation, params);
    result.textContent = JSON.stringify(response, null, 2);
    if (operation === 'query_knowledge') document.getElementById('knowledge-answer').textContent =
      response.outcome + ': ' + response.answer;
    if (operation === 'evidence') document.getElementById('details').open = true;
    message.textContent = operation === 'start_training'
      ? 'Training started. Refresh status to inspect progress.' : 'Local request completed. Review the recorded result.';
    await refresh();
  } catch (error) { message.textContent = error.message; }
  finally { for (const button of document.querySelectorAll('button')) button.disabled = false; }
}
document.querySelector('#connect').addEventListener('click', () => act('status'));
for (const button of document.querySelectorAll('[data-action]'))
  button.addEventListener('click', () => act(button.dataset.action));
