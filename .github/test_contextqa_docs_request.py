import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('docs_request',Path(__file__).parent/'contextqa_docs_request.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RequestTests(unittest.TestCase):
    def pr(self,n=1):return dict(number=18,changed_files=n,head={'sha':'a'*40},base={'repo':{'full_name':'nigharsh/kan'}})
    def test_card_change_requests_capture_without_execution(self):
        r=m.plan_request(self.pr(),[{'filename':'packages/api/src/routers/card.ts'}])
        self.assertEqual(r['workflows'],['kan-create-card'])
        self.assertFalse(r['execution_started']);self.assertFalse(r['deployment_matches_head'])
    def test_incomplete_changes_rejected(self):
        with self.assertRaises(ValueError):m.plan_request(self.pr(2),[{'filename':'README.md'}])
    def test_wrong_deployment_rejected(self):
        with self.assertRaises(ValueError):m.plan_request(self.pr(),[{'filename':'README.md'}],'b'*40)
    def test_renamed_affected_file_remains_mapped(self):
        r=m.plan_request(self.pr(),[{'filename':'new/file.ts','previous_filename':'packages/api/src/routers/card.ts'}],'a'*40)
        self.assertEqual(r['workflows'],['kan-create-card']);self.assertTrue(r['deployment_matches_head'])
    def test_unrelated_change_does_not_queue_capture(self):
        r=m.plan_request(self.pr(),[{'filename':'README.md'}])
        self.assertEqual(r['workflows'],[])
    def test_foreign_repo_rejected(self):
        pr=self.pr();pr['base']['repo']['full_name']='other/repo'
        with self.assertRaises(ValueError):m.plan_request(pr,[{'filename':'README.md'}])

    def test_list_backend_requires_recapture(self):
        for path in ['packages/api/src/routers/list.ts', 'packages/db/src/repository/list.repo.ts']:
            with self.subTest(path=path):
                r=m.plan_request(self.pr(),[{'filename':path}])
                self.assertEqual(r['workflows'],['kan-create-list'])
    def test_new_list_form_requires_list_recapture(self):
        r=m.plan_request(self.pr(),[{'filename':'apps/web/src/views/board/components/NewListForm.tsx'}])
        self.assertIn('kan-create-list',r['workflows'])
    def test_duplicate_files_cannot_satisfy_completeness(self):
        with self.assertRaises(ValueError):
            m.plan_request(self.pr(2),[{'filename':'README.md'}]*2)
    def test_changed_head_rejected(self):
        with self.assertRaises(ValueError):
            m.plan_request(self.pr(),[{'filename':'README.md'}],expected_head_sha='b'*40)
    def test_matching_sha_is_not_deployment_attestation(self):
        r=m.plan_request(self.pr(),[{'filename':'README.md'}],deployed_sha='a'*40)
        self.assertTrue(r['deployment_matches_head'])
        self.assertFalse(r['deployment_verified'])
    def test_invalid_previous_filename_rejected(self):
        with self.assertRaises(ValueError):
            m.plan_request(self.pr(),[{'filename':'README.md','previous_filename':42}])
