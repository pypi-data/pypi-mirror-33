# bids_events

Tool to export events from presentation log files.

## Installation

```
pip install bids_events
```

## Example of use

```python
from bids_events.presentation import LogHandler as Log

cols = [
    ['trial_type', Log.COL_CODE, r'cue.*'],
    ['fix_after_cue', Log.COL_CODE, r'fixAfterCue', Log.COL_TIME],
    ['reward', Log.COL_CODE, r'rew.*', Log.COL_CODE],
    ['response', Log.COL_CODE, r'press', Log.COL_TTIME],
    ['fix2', Log.COL_CODE, r'fix2', Log.COL_TTIME]
]

log = Log('S001-Run1.log')
log.extract_trials( cols )
log.export_bids('sub-S001_task-emotion_run-1')
```
