import json
import os


def increment_key(outdir, key):
    test_state_db = os.path.join(outdir, 'state.json')

    if os.path.exists(test_state_db):
        with open(test_state_db) as f:
            data = json.load(f)
    else:
        data = {}

    post_run_count = data.get(key, 0)
    post_run_count += 1
    data[key] = post_run_count

    with open(test_state_db, 'w') as f:
        json.dump(data, f)
