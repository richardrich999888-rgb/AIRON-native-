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
async function refresh() { state = await call('status'); }
async function act(operation) {
  for (const button of document.querySelectorAll('button')) button.disabled = true;
  message.textContent = 'Working locally…';
  try {
    await refresh();
    let params = {};
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
    message.textContent = operation === 'start_training'
      ? 'Training started. Refresh status to inspect progress.' : 'Local request completed. Review the recorded result.';
    await refresh();
  } catch (error) { message.textContent = error.message; }
  finally { for (const button of document.querySelectorAll('button')) button.disabled = false; }
}
document.querySelector('#connect').addEventListener('click', () => act('status'));
for (const button of document.querySelectorAll('[data-action]'))
  button.addEventListener('click', () => act(button.dataset.action));
