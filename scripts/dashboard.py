#!/usr/bin/python

import argparse
import datetime
import json
import logging
import os

import yaml

from httplib import ACCEPTED, HTTPConnection, HTTPException, OK, CREATED
from urllib import urlencode
from urlparse import urlparse

log = logging.getLogger()


class API(object):
    def __init__(self, host=None, port=None, user=None, key=None, prefix=None):
        if not host:
            host = os.environ.get('DASHBOARD_HOST', None)
        if not port:
            port = int(os.environ.get('DASHBOARD_PORT', '80'))
        if not user:
            user = os.environ.get('DASHBOARD_USER', None)
        if not key:
            key = os.environ.get('DASHBOARD_KEY', None)
        if not prefix:
            prefix = os.environ.get('DASHBOARD_PREFIX', None)

        self.host = host
        self.port = port
        self.resource_base = prefix

        self._headers = None
        if user and key:
            self._headers = {
                'Content-Type': 'application/json',
                'Authorization': 'ApiKey %s:%s' % (user, key)
            }
            # mod_wsgi will strip the Authorization header, but tastypie
            # allows it as GET param also. More details for fixing apache:
            #  http://django-tastypie.rtfd.org/en/latest/authentication.html
            self._auth_param = '?username=%s&api_key=%s' % (user, key)

    def _connect(self):
        if self.host:
            return HTTPConnection(self.host, self.port)
        return None

    def _http_get(self, resource):
        con = self._connect()
        if not con:
            # we just mock this for the case where the caller wants to
            # use our API transparently enabled/disabled
            return {}

        if self.resource_base:
            resource = self.resource_base + resource

        logging.debug('doing get on: %s', resource)
        headers = {'Content-Type': 'application/json'}
        con.request('GET', resource, headers=headers)
        resp = con.getresponse()
        if resp.status != OK:
            msg = ''
            try:
                msg = resp.read().decode()
            except:
                pass
            fmt = '%d error getting resource(%s): %s'
            raise HTTPException(fmt % (resp.status, resource, msg))
        data = json.loads(resp.read().decode())
        if len(data['objects']) == 0:
            raise HTTPException('resource not found: %s' % resource)
        assert len(data['objects']) == 1
        return data['objects'][0]['resource_uri']

    def _http_post(self, resource, params):
        con = self._connect()
        if not con or not self._headers:
            return None

        if self.resource_base:
            resource = self.resource_base + resource
        resource += self._auth_param

        params = json.dumps(params)
        log.debug('posting (%s): %s', resource, params)
        con.request('POST', resource, params, self._headers)
        resp = con.getresponse()
        if resp.status != CREATED:
            msg = ''
            try:
                msg = str(resp.getheaders())
                msg += resp.read().decode()
            except:
                pass
            raise HTTPException(
                '%d creating resource(%s): %s' % (resp.status, resource, msg))
        uri = resp.getheader('Location')
        return urlparse(uri).path

    def _http_patch(self, resource, params):
        con = self._connect()
        if not con or not self._headers:
            return None

        resource += self._auth_param

        con.request('PATCH', resource, json.dumps(params), self._headers)
        resp = con.getresponse()
        if resp.status != ACCEPTED:
            msg = ''
            try:
                msg = resp.getheaders()
            except:
                pass
            raise HTTPException(
                '%d patching resource(%s): %s' % (resp.status, resource, msg))
        return resource

    @staticmethod
    def _uri_to_pk(resource_uri):
        if resource_uri:
            return resource_uri.split('/')[-2]
        return None  # we are mocked

    def job_get(self, name):
        resource = '/smokeng/api/v1/job/?' + urlencode({'name': name})
        return self._http_get(resource)

    def job_add(self, name):
        resource = '/smokeng/api/v1/job/'
        params = {
            'name': name,
            'url': 'http://jenkins.qa.ubuntu.com/job/' + name + '/'
        }
        return self._http_post(resource, params)

    def build_add(self, job_name, job_number):
        try:
            logging.debug('trying to find job: %s', job_name)
            job = self.job_get(job_name)
        except HTTPException:
            job = self.job_add(job_name)
        logging.info('job is: %s', job)

        resource = '/smokeng/api/v1/build/'
        params = {
            'build_number': job_number,
            'job': job,
            'ran_at': datetime.datetime.now().isoformat(),
            'build_description': 'inprogress',
        }
        return self._http_post(resource, params)

    def _image_get(self, build_number, release, variant, arch, flavor):
        resource = '/smokeng/api/v1/image/?'
        resource += urlencode({
            'build_number': build_number,
            'release': release,
            'flavor': flavor,
            'variant': variant,
            'arch': arch,
        })
        return self._http_get(resource)

    def image_add(self, build_number, release, variant, arch, flavor):
        try:
            img = self._image_get(build_number, release, variant, arch, flavor)
            return img
        except HTTPException:
            # image doesn't exist so go continue and create
            pass

        resource = '/smokeng/api/v1/image/'
        params = {
            'build_number': build_number,
            'release': release,
            'flavor': flavor,
            'variant': variant,
            'arch': arch,
        }
        try:
            return self._http_post(resource, params)
        except HTTPException:
            # race situation. Both callers saw _image_get fail and tried to
            # create. Only one of them can succeed, so the failed call should
            # now safely be able to get the image created by the other
            img = self._image_get(build_number, release, variant, arch, flavor)
            return img

    def result_get(self, image, test):
        # deal with getting resource uri's as parameters instead of id's
        image = API._uri_to_pk(image)

        resource = '/smokeng/api/v1/result/?'
        resource += urlencode({
            'image': image,
            'name': test,
        })
        return self._http_get(resource)

    def _result_status(self, image, build, test, status, results=None):
        create = False
        params = {
            'ran_at': datetime.datetime.now().isoformat(),
            'status': status,
            'jenkins_build': build,
        }
        if results:
            params['results'] = results

        try:
            resource = self.result_get(image, test)
        except HTTPException:
            create = True
            resource = '/smokeng/api/v1/result/'
            params['image'] = image
            params['name'] = test

        if create:
            return self._http_post(resource, params)
        else:
            return self._http_patch(resource, params)

    def result_queue(self, image, build, test):
        return self._result_status(image, build, test, 0)

    def result_running(self, image, build, test):
        return self._result_status(image, build, test, 1)

    def result_syncing(self, image, build, test, results):
        return self._result_status(image, build, test, 2, results)


def _result_running(api, args):
    return api.result_running(args.image, args.build, args.test)


def _result_syncing(api, args):
    results = {}
    with open(args.results) as f:
        results = yaml.safe_load(f.read())
    return api.result_syncing(args.image, args.build, args.test, results)


def _set_args(parser, names, func):
    for n in names:
        parser.add_argument(n, required=True)
    parser.set_defaults(func=func)


def _get_parser():
    parser = argparse.ArgumentParser(
        description='Interact with the CI dashboard API')

    sub = parser.add_subparsers(title='Commands', metavar='')

    args = ['--image', '--build', '--test']
    p = sub.add_parser('result-running', help='Set a SmokeResult "Running".')
    _set_args(p, args, _result_running)

    p = sub.add_parser('result-syncing', help='Set a SmokeResult "Syncing".')
    _set_args(p, args, _result_syncing)
    p.add_argument('--results', required=True, help='UTAH yaml file')

    return parser


def _assert_env():
    required = [
        'DASHBOARD_HOST', 'DASHBOARD_PORT', 'DASHBOARD_USER', 'DASHBOARD_KEY']
    missing = []
    for r in required:
        if r not in os.environ:
            missing.append(r)
    if len(missing):
        print('Missing the following environment variables:')
        for x in missing:
            print('  %s' % x)
        exit(1)


def _main(args):
    _assert_env()

    api = API()
    try:
        val = args.func(api, args)
        if val:
            if '/?' in val:
                log.debug('stripping api-key from response')
                val = val.split('/?')[0] + '/'
            print(val)
    except HTTPException as e:
        print('ERROR: %s' % e)
        exit(1)

    exit(0)

if __name__ == '__main__':
    args = _get_parser().parse_args()
    exit(_main(args))
