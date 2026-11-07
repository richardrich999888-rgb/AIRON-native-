import {sha256} from './sha256.ts';
export type Role = 'analyst' | 'operator' | 'admin';
export type Outcome = 'ANSWERED' | 'DENIED' | 'ABSTAINED' | 'ERROR';
export type SourceDoc = { id:string; title:string; category:string; version:string; roles:Role[]; body:string; questions:string[] };
export const documents:SourceDoc[] = [
 {id:'OPS-001',title:'Equipment inspection protocol',category:'Operations',version:'1.2',roles:['analyst','operator','admin'],body:'Inspect the cooling assembly every 200 operating hours. Record the inspection in the maintenance register. If vibration exceeds 4.5 mm/s, stop the equipment and notify the shift supervisor.',questions:['When should we inspect the cooling assembly?','What is the inspection interval for the cooling assembly?','How often should we inspect the cooling assembly?','When should the cooling assembly be inspected?']},
 {id:'OPS-002',title:'Incident escalation procedure',category:'Operations',version:'1.0',roles:['analyst','operator','admin'],body:'A severity-one incident must be reported to the duty manager within 15 minutes. Isolate the affected workstation and preserve the local execution logs. Resume operation only after written approval from the duty manager.',questions:['How do we escalate a severity-one incident?','What is the severity-one incident procedure?']},
 {id:'FIN-001',title:'Supplier payment controls',category:'Finance',version:'1.1',roles:['admin'],body:'Supplier payments above INR 100,000 require approval from both the finance controller and the procurement lead. The requester cannot approve their own payment. All approvals must be recorded before release.',questions:['Who approves large supplier payments?','Who approves supplier payments above INR 100,000?','What are the supplier payment controls?','Show the supplier payment controls.']},
 {id:'IT-001',title:'Offline update policy',category:'Infrastructure',version:'1.0',roles:['operator','admin'],body:'Transfer update bundles using approved removable media. Verify the manifest and checksum before installation. A designated administrator must approve each update. Keep the previous approved version available for rollback.',questions:['How are offline updates approved?','What is the offline update policy?']}
];
export const scenarios = [
 {id:'retrieve',title:'Grounded retrieval',subtitle:'Answer with an inspectable source',question:documents[0].questions[0],role:'analyst' as Role,expected:'ANSWERED',doc:'OPS-001'},
 {id:'restrict',title:'Restricted access',subtitle:'Stop a request outside the user’s role',question:documents[2].questions[0],role:'analyst' as Role,expected:'DENIED',doc:'FIN-001'},
 {id:'abstain',title:'Insufficient evidence',subtitle:'Decline to invent an answer',question:'What will our revenue be next quarter?',role:'analyst' as Role,expected:'ABSTAINED',doc:null}
];
export function normalize(s:string){return s.toLowerCase().replace(/[^a-z0-9]/g,'');}
export function retrieve(question:string,role:Role,enabledIds=documents.map(d=>d.id)){
 if(!['analyst','operator','admin'].includes(role)) return {outcome:'DENIED' as Outcome,answer:'Access denied. An authorized session role is required.',sources:[] as SourceDoc[],reason:'Unknown role; request stopped before inference.'};
 const doc=documents.find(d=>enabledIds.includes(d.id)&&d.questions.some(q=>normalize(q)===normalize(question)));
 if(!doc)return {outcome:'ABSTAINED' as Outcome,answer:'These documents don’t contain enough information to answer that.',sources:[] as SourceDoc[],reason:'No supported question matched the selected synthetic corpus. No model was called.'};
 if(!doc.roles.includes(role))return {outcome:'DENIED' as Outcome,answer:'You don’t have access to this document.',sources:[] as SourceDoc[],reason:'Role policy blocked the request before source content or inference was returned.'};
 return {outcome:'ANSWERED' as Outcome,answer:doc.body,sources:[doc],reason:'Exact supported-question match. Extractive response from authorized synthetic evidence.'};
}
export type RunRecord = {id:string;at:string;question:string;role:Role;outcome:Outcome;answer:string;reason:string;sources:{id:string;title:string;version:string;quote:string}[];mode:'rehearsal'|'local';durationMs:number;model:string|null;tokenCount:number|null;assurance:'CANNOT_PROVE';previousHash:string;hash:string;pilot:string;runtimeReceipt?:unknown};
export function canonical(value:unknown):string{
 if(value===null||typeof value!=='object')return JSON.stringify(value);
 if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
 return '{'+Object.keys(value as object).sort().map(k=>JSON.stringify(k)+':'+canonical((value as Record<string,unknown>)[k])).join(',')+'}';
}
export async function digest(value:unknown){const bytes=new TextEncoder().encode(canonical(value));return globalThis.crypto?.subtle?Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(b=>b.toString(16).padStart(2,'0')).join(''):sha256(bytes);}
export async function seal(record:Omit<RunRecord,'hash'>):Promise<RunRecord>{return {...record,hash:await digest(record)};}
export async function verifyRecords(records:RunRecord[]){
 let previous='GENESIS';
 for(const record of records){const {hash,...body}=record;if(body.previousHash!==previous||await digest(body)!==hash)return {valid:false,id:record.id};previous=hash;}
 return {valid:true,id:null};
}
export const capabilityRows = [
 ['Guided synthetic workflow','Implemented here','Browser','Three reproducible scenarios; deterministic answers.'],
 ['Retrieval and abstention','Implemented here','Browser + local','Exact supported-question matching; authorized source excerpts.'],
 ['Role restrictions','Implemented here','Demo scope','Client demonstration; local gateway enforces its assigned role.'],
 ['Execution record export','Implemented here','Local','SHA-256 chain, JSON export; unsigned and locally editable.'],
 ['Local model adapter','Awaiting verification','Local package','Ollama loopback adapter included; real-model acceptance is pending.'],
 ['Air-gap deployment','Awaiting verification','Pilot environment','Offline package included; isolation must be tested on target hardware.'],
 ['AIP accountability','Related work','Separate repository','README inspected; no AIP signing or verification wired into this console.'],
 ['Self-evolving intelligence','Planned','Research','No autonomous learning, weight updates or self-modification.'],
 ['Distributed model delivery','Planned','Roadmap','No peer-to-peer model distribution in this build.']
];
