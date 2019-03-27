#!/usr/bin/env python

import sys
import os
import re
import tarfile

import internetarchive as ia

import DB

class ArchiveUploader:
    DESCRIPTION = """{pkgdesc}

    This item contains old versions of the <a href="https://www.archlinux.org/packages/{pkgname}">Arch Linux package for {pkgname}</a>.
    Website of the upstream project: <a href="{url}">{url}</a>
    License: {license}
    See the <a href="https://wiki.archlinux.org/index.php/Arch_Linux_Archive">Arch Linux Archive documentation</a> for details.
    """

    def __init__(self, internetarchive = ia, db = DB.DB('archive-uploader.sqlite')):
        self.ia = internetarchive
        self.db = db

    def clean_name(self, name):
        """Remove chars that are not allowed in an Internet Archive identifier: @.+
        Only alphanumerics, - and _ and allowed."""
        res = name.replace('@', '_')
        res = res.replace('+', '_')
        res = res.replace('.', '_')
        return res

    def extract_pkginfo(self, package):
        """Given a package (.tar.xz filename), extract and parse its .PKGINFO file as a dict"""
        with tarfile.open(package, mode='r|*', encoding='utf-8') as tar:
            # Manual seeking to find .PKGINFO without having to uncompress the whole package
            while True:
                f = tar.next()
                if f.name == '.PKGINFO':
                    break
            pkginfo = tar.extractfile(f).readlines()
            # Parse .PKGINFO
            res = dict()
            for line in pkginfo:
                m = re.match(r'([^=]*) = (.*)', line.decode('utf8'))
                if m:
                    # TODO: support multi-valued attributes
                    key, value = m[1], m[2].strip()
                    res[key] = value
            return res

    def upload_pkg(self, identifier, pkgname, metadata, directory):
        """Upload all versions for package given by [directory]"""
        files = []
        for f in os.scandir(directory):
            filename = os.path.basename(f.path)
            if not self.db.exists(filename):
                files.append(f.path)
        if not files:
            return
        # Get last package, to extract a description
        last_pkg = sorted(filter(lambda x: not x.endswith('.sig'), files))[-1]
        pkginfo = self.extract_pkginfo(last_pkg)
        pkgdesc = pkginfo['pkgdesc'] if 'pkgdesc' in pkginfo else ''
        metadata['description'] = ArchiveUploader.DESCRIPTION.format(pkgname=pkgname, pkgdesc=pkgdesc, url=pkginfo['url'], license=pkginfo['license'])
        metadata['rights'] = 'License: ' + pkginfo['license']
        #print(pkgname, len(files))
        #print(metadata)
        try:
            res = self.ia.upload(identifier, files=files, metadata=metadata)
            if all([x.status_code == 200 for x in res]):
                for f in files:
                    if not f.endswith('.sig'):
                        filename = os.path.basename(f)
                        self.db.add_file(filename)
            else:
                ok = len([x for x in res if x.status_code == 200])
                nok = len([x for x in res if x.status_code != 200])
                codes = set([x.status_code for x in res])
                print("{}: only {}/{} files uploaded, status codes: {}".format(identifier, ok, ok+nok, codes), file=sys.stderr)
                print(directory)
        except Exception as e:
            print("{}: exception raised".format(identifier), file=sys.stderr)
            print(e, file=sys.stderr)
            print(directory)


    def main(self, pkg_dir):
        """Upload all versions of a single package"""
        pkgname = os.path.basename(pkg_dir)
        identifier = self.clean_name('archlinux_pkg_' + pkgname)
        metadata = {
            #'collection': ['test_collection', 'open_source_software'],
            #'collection': ['open_source_software'],
            'collection': ['archlinuxarchive'],
            'mediatype': 'software',
            'publisher': 'Arch Linux',
            'creator': 'Arch Linux',
            'subject': ['archlinux', 'archlinux package'],
        }
        metadata['title'] = pkgname + " package archive from Arch Linux"
        metadata['subject'].append(pkgname)
        self.upload_pkg(identifier, pkgname, metadata, pkg_dir)

if __name__ == '__main__':
    ArchiveUploader().main(sys.argv[1])
