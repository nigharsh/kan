"""Map a Kan PR to documentation recapture work. No execution or credentials."""
import argparse
import fnmatch
import json
import re
from pathlib import Path

RULES = {
    'kan-create-card': ['apps/web/src/views/board/**', 'apps/web/src/views/card/**', 'packages/api/src/routers/card.ts', 'packages/db/src/repository/card*'],
    'kan-checklist': ['apps/web/src/views/card/**', 'packages/api/src/routers/checklist*'],
    'kan-create-board': ['apps/web/src/views/boards/**', 'packages/api/src/routers/board*'],
}
SHARED = ['apps/web/src/components/**', 'packages/auth/**', 'apps/web/src/locales/**']


def plan_request(pr, files, deployed_sha=None):
    if pr.get('base', {}).get('repo', {}).get('full_name') != 'nigharsh/kan':
        raise ValueError('Expected the authorized nigharsh/kan repository')
    sha = pr.get('head', {}).get('sha', '')
    if not re.fullmatch('[a-f0-9]{40}', sha) or type(pr.get('number')) is not int or pr['number'] < 1:
        raise ValueError('A PR number and full head SHA are required')
    if not isinstance(files, list) or len(files) > 3000:
        raise ValueError('Expected a bounded complete changed-file list')
    if pr.get('changed_files') != len(files):
        raise ValueError('Changed-file list is incomplete; do not silently miss affected guides')
    paths = set()
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get('filename'), str):
            raise ValueError('Invalid changed-file record')
        paths.add(item['filename'])
        if item.get('previous_filename'):paths.add(item['previous_filename'])
    workflows = sorted(name for name, patterns in RULES.items() if any(fnmatch.fnmatchcase(path, pattern) for path in paths for pattern in patterns + SHARED))
    if deployed_sha is not None and deployed_sha != sha:
        raise ValueError('Deployment SHA does not match this PR head; refusing a misleading version label')
    return {
        'schema': 1, 'repository':'nigharsh/kan', 'pull_request':pr['number'], 'head_sha':sha,
        'target_url':'https://kan-qa.vercel.app/', 'requested_runner':'ContextQA Max',
        'workflows':workflows, 'changed_files':sorted(paths),
        'deployment_sha':deployed_sha, 'deployment_matches_head':deployed_sha == sha,
        'state':'capture_required' if workflows else 'no_mapped_workflow_changes',
        'execution_started':False, 'documentation_published':False,
        'requirements':['Resolve the requested runner against actual tenant settings.',
                        'Verify deployed commit before claiming this guide documents the PR.',
                        'Use an authorized Kan auth profile; never put credentials in this request.',
                        'Run selected workflows, collect real media, review, and compare with the baseline.'],
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pr',type=Path,required=True)
    p.add_argument('--files',type=Path,required=True)
    p.add_argument('--deployed-sha')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    request=plan_request(json.loads(a.pr.read_text()),json.loads(a.files.read_text()),a.deployed_sha)
    with a.out.open('x') as f:json.dump(request,f,indent=2);f.write('\n')
    print(json.dumps({k:request[k] for k in ['state','workflows','execution_started','deployment_matches_head']}))

if __name__=='__main__':main()
