#!env/bin/python

from optparse import OptionParser
from vps_ import main

# Version
version = '0.1.0'

# Command line argument parsing
descr = 'VPS v' + version
parser = OptionParser(usage='VPS-{}/vps <options>'.format(version), version=version, description=descr)
parser.add_option('--input', default=None, dest='input', action='store', help="Input VCF file")
parser.add_option('--output', default=None, dest='output', action='store', help="Output CSV file")
parser.add_option('--maxentscan', default=None, dest='maxentscan', action='store', help="MaxEntScan data file")
parser.add_option('--palist', default=None, dest='palist', action='store', help="PA list file")
parser.add_option('--geneconfig', default=None, dest='geneconfig', action='store', help="Gene config file")
parser.add_option('--gs', default=None, dest='gs', action='store', help="Google Scholar file")
parser.add_option('--exac', default=None, dest='exac', action='store', help="...")
parser.add_option('--gnomadex', default=None, dest='gnomadex', action='store', help="...")
parser.add_option('--gnomadgen', default=None, dest='gnomadgen', action='store', help="...")
parser.add_option('--curation', default=None, dest='curation', action='store', help="...")
parser.add_option('--common', default=None, dest='common', action='store', help="...")

(options, args) = parser.parse_args()

main.run(options, version)