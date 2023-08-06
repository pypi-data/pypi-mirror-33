import re

# Class to manipulate presentation logs
class LogParser:
    def __init__(self, file):
        self.file = file
        self.extract_data()

    # Do extraction of all data
    def extract_data(self):
        with open(self.file) as f:
            content = f.readlines()

        # Removing \n and split with \t
        content = [x.strip().split('\t') for x in content]
        self.raw = get_part(content, 'Subject')
        self.events = get_part(content, 'Event Type')

# Class to manipulate presentation logs
class LogHandler:
    COL_SUBJECT    = 0
    COL_TRIAL      = 1
    COL_EVENT_TYPE = 2
    COL_CODE       = 3
    COL_TIME       = 4
    COL_TTIME      = 5 
    COL_DURATION   = 7
    EMPTY_CELL     = 'n/a'

    def __init__(self, file):
        log = LogParser(file)
        self.raw    = log.raw
        self.events = log.events

    def get_first_pulse_time(self):
        pulses = filter_lines(self.raw, self.COL_EVENT_TYPE, r'Pulse')
        return int( pulses[0][1][self.COL_TIME] )

    def fix_times(self):
        first_pulse = self.get_first_pulse_time()
        for i in range(2,len(self.raw)):
            line = self.raw[i]
            line[self.COL_TIME] = float(line[self.COL_TIME]) - first_pulse
            line[self.COL_TIME] /= 10000
            line[self.COL_TTIME] = float(line[self.COL_TTIME]) / 10000
            try:
                line[self.COL_DURATION] = float(line[self.COL_DURATION]) / 10000
            except:
                pass
            self.raw[i] = line

    # Do extraction of all data
    def extract_trials(self, cols):
        self.fix_times()
        trials = filter_lines(self.raw, cols[0][1], cols[0][2])
        
        header = ['onset', 'duration']
        header.extend([i[0] for i in cols]) # Adding extra columns
        vals = []

        n_trials = len(trials)
        for n in range(n_trials):
            trial = trials[n][1]
            onset = trial[self.COL_TIME]
            duration = trial[self.COL_DURATION]
            code = trial[self.COL_CODE]

            # First column is mandatory (used to extract trial onset)
            first = trials[n][0]
            last = len(self.raw) if n == n_trials-1 else trials[n+1][0]

            # Ignoring first column (trial onset)
            extras = []
            for col in cols[1:]:
                item = filter_lines(self.raw[first:last], col[1], col[2])
                try:
                    content = item[0][1][col[3]]
                except:
                    content = self.EMPTY_CELL
                extras.extend([content])

            vals.append([onset, duration, code] + extras)
        
        # Returning all data
        self.trials = [header] + vals

    def export_bids(self, filename):
        output = ''
        for line in self.trials:
            output += "\t".join([str(i) for i in line]) + "\n"

        # Generating output
        with open('{}_events.tsv'.format(filename), 'w') as f:
            f.write(output)

    def write_raw(self):
        report(self.raw)

    def write_events(self):
        report(self.events)


## GENERAL FUNCTIONS
def filter_lines(content, column, rfilter):
    return filter(lambda (i,x): re.findall(rfilter, x[column]), enumerate(content))

def report(content):
    for line in content:
        print( '\t'.join(line) )

# Extract header position
def header_line(content, first_col):
    n_lines = len(content)
    for n_line in range(n_lines):
        if content[n_line][0] == first_col and content[n_line+1][0] == '':
            return n_line
    return None

# Extract table last position
def last_line(content, first_line):
    n_lines = len(content)
    for n_line in range(first_line, n_lines):
        if content[n_line][0] == '':
            return n_line-1
    return n_lines-1

# Extract parts of the file
def get_part(content, first_col):
    n_header = header_line(content, first_col)
    n_end = last_line(content, n_header+2)
    data = [content[n_header]]
    data.extend( content[ n_header+2:n_end ] )
    return data