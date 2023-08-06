from collections import namedtuple


JobCreated = namedtuple('JobCreated', ['handle'])
JobAssign = namedtuple('JobAssign', ['handle', 'function', 'workload'])
JobAssignUniq = namedtuple('JobAssignUniq', ['handle', 'function', 'uuid', 'workload'])
JobAssignAll = namedtuple('JobAssignAll', ['handle', 'function', 'uuid', 'reducer', 'workload'])
WorkComplete = namedtuple('WorkComplete', ['handle', 'result'])
WorkData = namedtuple('WorkData', ['handle', 'data'])
WorkFail = namedtuple('WorkFail', ['handle'])
WorkException = namedtuple('WorkException', ['handle', 'exception'])
NoJob = namedtuple('NoJob', [])
Noop = namedtuple('Noop', [])
StatusRes = namedtuple('StatusRes', ['handle', 'known', 'running', 'numerator', 'denominator'])
StatusResUnique = namedtuple(
    'StatusResUnique', ['handle', 'known', 'running', 'numerator', 'denominator', 'waiting'])
