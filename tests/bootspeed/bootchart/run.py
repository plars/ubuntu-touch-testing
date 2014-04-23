#!/usr/bin/python

import datetime
import json
import os
import shutil
import subprocess


def _get_dashboard_data(timing_file):
    info = subprocess.check_output(['adb', 'shell', 'system-image-cli', '-i'])
    data = {
        'image_md5': 'n/a',
        'machine_mac': 'ff:ff:ff:ff:ff:ff',
        'ran_at': datetime.datetime.now().isoformat(),
        'kernel_init': 0.0,
    }
    for line in info.split('\r\n'):
        if not line:
            continue
        key, val = line.split(':', 1)
        val = val.strip()
        if key == 'device name':
            data['image_arch'] = val
        elif key == 'channel':
            # get 'touch' and 'trusty' from something like:
            # ubuntu-touch/trusty-proposed
            variant, release = val.split('/')
            data['image_variant'] = variant.split('-')[1]
            data['image_release'] = release.split('-')[0]
        elif key == 'version version':
            data['number'] = val
        elif key == 'version ubuntu':
            data['version_ubuntu'] = val
        elif key == 'version device':
            data['version_device'] = val
    data['build_number'] = '%s:%s:%s' % (
        data['number'], data['version_ubuntu'], data['version_device'])

    with open(timing_file) as f:
        # the timings file is sequence of readings (in hundredths of a second):
        #  line 0 - the total boot time
        #  line X - the time from boot until the given annotation *started*
        timings = [float(x) / 100.0 for x in f.read().split('\n') if x]
        data['boot'] = timings[0]
        data['kernel'] = timings[1]
        data['plumbing'] = timings[2] - timings[1]
        data['xorg'] = timings[3] - timings[2]
        data['desktop'] = timings[0] - timings[3]
    return data


def chart(results_dir):
    timings = os.path.join(results_dir, 'timings')
    os.environ['CHARTOPTS'] = ' '.join([
        '--crop-after=unity8',
        '--annotate=mountall',
        '--annotate=lightdm',
        '--annotate=unity8',
        '--annotate-file=%s' % timings,
    ])
    subprocess.check_call(['phablet-bootchart', '-n', '-k',
                           '-w', '/home/ubuntu/magners-wifi',
                           '-o', results_dir])
    data = _get_dashboard_data(timings)
    with open(os.path.join(results_dir, 'boot.json'), 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    if os.path.exists('/tmp/results'):
        shutil.rmtree('/tmp/results')
    os.mkdir('/tmp/results')
    for x in range(3):
        chart('/tmp/results/%d' % (x + 1))
