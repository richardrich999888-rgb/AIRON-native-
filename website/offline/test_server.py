import unittest
from server import retrieve,validate_model_response,DOCS
class PolicyTests(unittest.TestCase):
    def test_authorized(self):self.assertEqual(retrieve(DOCS[0]['questions'][0],'analyst',['OPS-001'])['outcome'],'ANSWERED')
    def test_restricted(self):
        r=retrieve(DOCS[2]['questions'][0],'analyst',['FIN-001']);self.assertEqual(r['outcome'],'DENIED');self.assertEqual(r['sources'],[]);self.assertNotIn('procurement lead',str(r))
    def test_admin(self):self.assertEqual(retrieve(DOCS[2]['questions'][0],'admin',['FIN-001'])['outcome'],'ANSWERED')
    def test_unknown(self):self.assertEqual(retrieve('What will revenue be?','analyst',[d['id'] for d in DOCS])['outcome'],'ABSTAINED')
    def test_unknown_role(self):self.assertEqual(retrieve(DOCS[0]['questions'][0],'visitor',['OPS-001'])['outcome'],'DENIED')
    def test_disabled_source(self):self.assertEqual(retrieve(DOCS[0]['questions'][0],'analyst',[])['outcome'],'ABSTAINED')
    def test_model_validation(self):
        import json
        d=DOCS[0]
        self.assertTrue(validate_model_response({'done':True,'message':{'content':json.dumps({'source_id':d['id'],'quote':d['body']})}},d))
        for content in ('invented',json.dumps({'source_id':d['id'],'quote':'made up'}),json.dumps({'source_id':'WRONG','quote':d['body']})):
            self.assertFalse(validate_model_response({'done':True,'message':{'content':content}},d))
if __name__=='__main__':unittest.main()

class HTTPGatewayTests(unittest.TestCase):
    def setUp(self):
        import server,threading,tempfile,pathlib
        self.tmp=tempfile.TemporaryDirectory();self.gateway=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Gateway)
        self.gateway.token='test-only-token';self.gateway.role='analyst';self.gateway.model='test-local';self.gateway.query_lock=threading.Lock();self.gateway.previous_hash='GENESIS';self.gateway.log_path=pathlib.Path(self.tmp.name)/'records.jsonl'
        self.thread=threading.Thread(target=self.gateway.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):self.gateway.shutdown();self.gateway.server_close();self.thread.join();self.tmp.cleanup()
    def request(self,path,body=None,token='test-only-token',origin=None):
        import urllib.request,urllib.error,json
        headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        req=urllib.request.Request('http://127.0.0.1:'+str(self.gateway.server_port)+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
        try:
            with urllib.request.urlopen(req) as response:return response.status,json.loads(response.read())
        except urllib.error.HTTPError as e:return e.code,json.loads(e.read())
    def test_pairing_token_required(self):self.assertEqual(self.request('/api/health',token='wrong')[0],401)
    def test_cross_origin_blocked(self):self.assertEqual(self.request('/api/health',origin='https://untrusted.example')[0],403)
    def test_client_cannot_escalate_role(self):
        from unittest.mock import patch
        with patch('server.ollama') as model:
            code,result=self.request('/api/query',{'question':DOCS[2]['questions'][0],'enabled':['FIN-001'],'role':'admin'})
            self.assertEqual(code,200);self.assertEqual(result['outcome'],'DENIED');self.assertEqual(result['receipt']['role'],'analyst');self.assertEqual(result['sources'],[]);model.assert_not_called()
    def test_invalid_request_blocked(self):self.assertEqual(self.request('/api/query',{'question':'hello','enabled':['PRIVATE']})[0],400)
    def test_health_uses_exact_installed_model(self):
        from unittest.mock import patch
        with patch('server.ollama',return_value={'models':[{'name':'test-local','digest':'mock-digest'}]}):
            code,result=self.request('/api/health');self.assertEqual(code,200);self.assertTrue(result['available']);self.assertEqual(result['digest'],'mock-digest')
    def test_validated_model_quote_and_record(self):
        import json
        from unittest.mock import patch
        d=DOCS[0]
        responses=[{'models':[{'name':'test-local','digest':'mock-digest'}]},{'done':True,'eval_count':30,'message':{'content':json.dumps({'source_id':d['id'],'quote':d['body']})}}]
        with patch('server.ollama',side_effect=responses):
            code,result=self.request('/api/query',{'question':d['questions'][0],'enabled':[d['id']]});self.assertEqual(code,200);self.assertEqual(result['answer'],d['body']);self.assertEqual(result['tokenCount'],30)
            record=json.loads(self.gateway.log_path.read_text());self.assertEqual(record['hash'],result['receipt']['hash']);self.assertEqual(record['assurance'],'CANNOT_PROVE')
    def test_model_failure_never_falls_back(self):
        from unittest.mock import patch
        with patch('server.ollama',side_effect=OSError('unavailable')):
            code,result=self.request('/api/query',{'question':DOCS[0]['questions'][0],'enabled':['OPS-001']});self.assertEqual(code,200);self.assertEqual(result['outcome'],'ERROR');self.assertEqual(result['sources'],[])
    def test_model_hallucination_withheld(self):
        from unittest.mock import patch
        with patch('server.ollama',side_effect=[{'models':[{'name':'test-local'}]},{'done':True,'message':{'content':'{"source_id":"OPS-001","quote":"invented answer"}'}}]):
            code,result=self.request('/api/query',{'question':DOCS[0]['questions'][0],'enabled':['OPS-001']});self.assertEqual(result['outcome'],'ABSTAINED');self.assertNotIn('invented answer',result['answer'])
