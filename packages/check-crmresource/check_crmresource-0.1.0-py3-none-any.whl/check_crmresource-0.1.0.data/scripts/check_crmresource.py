#!python

import io
import subprocess
import argparse
import re

import nagiosplugin


class SingleResource(nagiosplugin.Resource):
    name = 'CRM_RESOURCE'

    def __init__(self, *args, **kwargs):
        self.resource = kwargs.pop('resource')
        super(nagiosplugin.Resource, self).__init__(*args, **kwargs)

    def probe(self):
        resources = get_crm_resources()
        for resource in resources:
            if resource['name'] == self.resource:
                yield nagiosplugin.Metric(resource['identifier'], resource['state'], context='crmresource')


class AllResources(nagiosplugin.Resource):
    name = 'CRM_RESOURCE'

    def probe(self):
        resources = get_crm_resources()
        for resource in resources:
            yield nagiosplugin.Metric(resource['identifier'], resource['state'], context='crmresource')


class CRMResourceContext(nagiosplugin.Context):

    def __init__(self):
        super(CRMResourceContext, self).__init__('crmresource')

    def evaluate(self, metric, resource):
        if metric.value == 'Started':
            return self.result_cls(nagiosplugin.state.Ok, metric=metric, hint=metric.name + ': ' + metric.value)
        else:
            return self.result_cls(nagiosplugin.state.Critical, metric=metric, hint=metric.name + ': ' + metric.value)


class CRMResourceSummary(nagiosplugin.Summary):

    def ok(self, results):
        return 'All resources started'

    def problem(self, results):
        return ', '.join(['{0}'.format(result) for result in results.most_significant])

    def verbose(self, results):
        return ['{0}: {1}'.format(result.state, result) for result in results]


def get_crm_resources():
    try:
        p = subprocess.Popen(['sudo', 'crm_resource', '--list'],
                             stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
    except OSError as e:
        raise nagiosplugin.CheckError(e)

    if stderr:
        raise nagiosplugin.CheckError(stderr)

    resources = []
    if stdout:
        for line in io.StringIO(stdout.decode('utf-8')):
            split_line = line.split()
            if len(split_line) != 3:
                continue
            resource_name, resource_type, resource_state = split_line
            m = re.match(r'(?P<resource_type>\(.*\))(?=:)', resource_type)
            if m:
                resources.append({'name': resource_name,
                                  'type': m.group('resource_type').strip('(').strip(')'),
                                  'state': resource_state,
                                  'identifier': resource_name + ' ' + m.group('resource_type')})
    return resources


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--resource", type=str, dest="resource", help="Name of the resource that is beeing tested")
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase output verbosity (use up to 3 times)')

    args = parser.parse_args()

    if args.resource is None:
        check = nagiosplugin.Check(
            AllResources(),
            CRMResourceContext(),
            CRMResourceSummary())
    else:
        check = nagiosplugin.Check(
            SingleResource(resource=args.resource),
            CRMResourceContext())
    check.main(args.verbose)

if __name__ == '__main__':
    main()
