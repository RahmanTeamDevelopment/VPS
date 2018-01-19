
import process
import parsers
import sys
import datetime


def print_info(options):

    lines = [
        'MaxEntScan data:       ' + options.maxentscan,
        'PA list:               ' + options.palist,
        'Gene config:           ' + options.geneconfig,
        'Google Scholar:        ' + options.gs,
        'ExAC data:             ' + options.exac,
        'gnomAD exomes data:    ' + options.gnomadex,
        'gnomAD genomes data:   ' + options.gnomadgen,
        'Curation data:         ' + options.curation,
        'Common variants data:  ' + options.common
    ]

    N = min(max([len(x) for x in lines]), 99)
    print '-'*N
    for l in lines:
        print l
    print '-'*N+'\n'


def run(options, version):

    print '\n'+'='*100
    print 'Variant Prioritisation System (VPS) {} is running'.format(version)
    now = str(datetime.datetime.now())
    now = now[:now.find('.')]
    print 'Started: {}\n'.format(now)

    print_info(options)

    out = open(options.output + '.csv', 'w')

    data = parsers.read_data(options)

    process.initialize_csv_file(out, data['pa_column_names'])

    sys.stdout.write('Processing input file ... ')
    sys.stdout.flush()
    for line in open(options.input):
        line = line.strip()
        if line == '' or line[0] == '#':
            continue

        chrom, pos, ref, alts, gene, csn, class_, cart = parsers.parse_VCF_record(line)

        for alt in alts:
            if len(alt) == 1 and len(ref) == 1:
                record = process.column_values(data, chrom, pos, ref, alt, gene, csn, class_)
                process.output_to_csv(out, chrom, pos, ref, alt, gene, csn, class_, cart, record)

    out.close()
    print 'done'

    print '\nOutput file created: {}.csv'.format(options.output)

    now = str(datetime.datetime.now())
    now = now[:now.find('.')]
    print '\nFinished: {}'.format(now)
    print '='*100+'\n'
