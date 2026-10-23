from fastapi.testclient import TestClient
from app.main import app


def test_health_is_honest_about_integrations():
    with TestClient(app) as client:
        data = client.get('/api/health').json()
    assert data['ok'] is True
    assert data['policy_mode'] in {'local', 'aws_avp'}
    assert 'note' in data
    if not data['mcp_sdk_available']:
        assert data['mcp_endpoint'] is None


def test_access_denial_and_allow_are_audited(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'audit.sqlite3'))
    with TestClient(app) as client:
        denied = client.post('/api/access', json={
            'principal_role': 'visitor', 'door_id': 'FRONT-01',
            'reason': 'Package delivery', 'verified_identity': False
        }).json()
        allowed = client.post('/api/access', json={
            'principal_role': 'resident', 'door_id': 'FRONT-01',
            'reason': 'Resident entry', 'verified_identity': True, 'homeowner_approved': True
        }).json()
        events = client.get('/api/audit').json()['events']
    assert denied['decision'] == 'DENY'
    assert allowed['decision'] == 'ALLOW'
    assert allowed['simulated_grant_preview']['max_entries'] == 1
    assert allowed['simulated_grant_preview']['valid_for_minutes'] == 15
    assert denied['simulated_grant_preview'] is None
    assert len(events) == 2
    assert {e['decision'] for e in events} == {'ALLOW', 'DENY'}


def test_case_lookup_and_proposal_do_not_execute_external_actions(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'audit.sqlite3'))
    with TestClient(app) as client:
        case = client.post('/api/case', json={'case_id': 'CASE-1042', 'principal_role': 'resident'}).json()
        proposal = client.post('/api/proposal', json={
            'case_id': 'CASE-1042', 'action': 'Schedule inspection',
            'rationale': 'Inspect the reported issue', 'principal_role': 'support_agent'
        }).json()
    assert case['ok'] is True
    assert proposal['status'] == 'PROPOSED_NOT_EXECUTED'
    assert proposal['safety_note'].startswith('Proposal recorded only')


def test_workflow_preview_requires_separate_one_time_approval(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'workflow.sqlite3'))
    with TestClient(app) as client:
        preview = client.post('/api/workflow', json={
            'case_id': 'CASE-1042',
            'request': 'Arrange a plumber visit and ask before granting entry.',
        }).json()
        assert preview['status'] == 'AWAITING_HUMAN_APPROVAL'
        assert len(preview['steps']) == 3
        assert preview['steps'][2]['result']['decision'] == 'PENDING'
        denied = client.post('/api/workflow/approve', json={
            'run_id': preview['run_id'], 'action_hash': preview['action_hash'], 'verified_identity': False
        }).json()
        replay = client.post('/api/workflow/approve', json={
            'run_id': preview['run_id'], 'action_hash': preview['action_hash'], 'verified_identity': True
        }).json()
        events = client.get('/api/audit').json()['events']
    assert denied['status'] == 'DENIED'
    assert denied['access_decision']['decision'] == 'DENY'
    assert replay['status'] == 'ALREADY_FINALIZED'
    assert len(events) >= 3
    assert 'no physical lock was operated' in denied['safety_boundary']


def test_approved_workflow_returns_scoped_preview_but_never_executes(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'workflow-approved.sqlite3'))
    with TestClient(app) as client:
        preview = client.post('/api/workflow', json={
            'case_id': 'CASE-1042', 'request': 'Arrange a plumber visit with approved entry.'
        }).json()
        mismatch = client.post('/api/workflow/approve', json={
            'run_id': preview['run_id'], 'action_hash': '0' * 64, 'verified_identity': True
        }).json()
        approved = client.post('/api/workflow/approve', json={
            'run_id': preview['run_id'], 'action_hash': preview['action_hash'], 'verified_identity': True
        }).json()
    assert approved['status'] == 'APPROVED_SIMULATED'
    assert approved['access_decision']['decision'] == 'ALLOW'
    assert approved['access_decision']['simulated_grant_preview']['max_entries'] == 1
    assert approved['access_decision']['simulated_grant_preview']['valid_for_minutes'] == 15
    assert approved['access_decision']['execution'] == 'SIMULATED_ONLY'
    assert mismatch['status'] == 'HASH_MISMATCH'


def test_workflow_hash_changes_when_request_changes(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'hash-binding.sqlite3'))
    with TestClient(app) as client:
        one = client.post('/api/workflow', json={'case_id': 'CASE-1042', 'request': 'Arrange a plumber visit.'}).json()
        two = client.post('/api/workflow', json={'case_id': 'CASE-1042', 'request': 'Arrange a smoke alarm battery replacement.'}).json()
    assert one['action_hash'] != two['action_hash']
