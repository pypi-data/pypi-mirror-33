import os
import sys
import argparse

import synapse.telepath as s_telepath

import synapse.lib.output as s_output

def getArgParser():
    p = argparse.ArgumentParser()
    p.add_argument('cortex', help='telepath URL for a target cortex')
    p.add_argument('filenames', nargs='+', help='files to upload')
    p.add_argument('--tags', help='comma separated list of tags to add to the nodes')
    return p

def main(argv, outp=None):

    if outp is None:  # pragma: no cover
        outp = s_output.OutPut()

    p = getArgParser()
    opts = p.parse_args(argv)

    core = s_telepath.openurl(opts.cortex)

    tags = []
    if opts.tags:
        for tag in opts.tags.split(','):
            tags.append(tag)

    if tags:
        outp.printf('adding tags: %r' % (tags,))

    for path in opts.filenames:

        with open(path, 'rb') as fd:

            base = os.path.basename(path)
            node = core.formNodeByFd(fd, name=base)

            core.addTufoTags(node, tags)

            iden = node[1].get('file:bytes')
            size = node[1].get('file:bytes:size')
            name = node[1].get('file:bytes:name')

            outp.printf('file: %s (%d) added (%s) as %s' % (base, size, iden, name))

    core.fini()  # Shut down the proxy

if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
