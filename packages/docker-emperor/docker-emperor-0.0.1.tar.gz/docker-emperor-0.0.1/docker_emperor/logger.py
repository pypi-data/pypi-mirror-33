
HEADER = '\033[95m'
LHEADER = '\033[1;95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
GREEN = OKGREEN
WARNING = '\033[93m'
YELLOW = WARNING
LYELLOW = '\033[1;93m'
ERROR = '\033[91m'
LERROR = '\033[1;91m'
END = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def success(*value):
    value = " ".join([str(v) for v in value])
    log('{}{}{}'.format(GREEN, value, END))

def info(*value):
    value = " ".join([str(v) for v in value])
    log('{}{}{}'.format(LHEADER, value, END))

def comment(*value):
    value = " ".join([str(v) for v in value])
    log('{}{}{}'.format(HEADER, value, END))

def warning(*value):
    value = " ".join([str(v) for v in value])
    log('{}{}{}'.format(WARNING, value, END))

def error(*value):
    value = " ".join([str(v) for v in value])
    log('{}{}{}'.format(ERROR, value, END))

def log(value):
    print(value.strip())