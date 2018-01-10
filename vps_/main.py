
import process
import parsers

def run(options, version):

    print '\n'+'='*100
    print 'Variant Prioritisation System (VPS) {} is running.\n'.format(version)

    out = open(options.output + '.csv', 'w')

    data = parsers.read_data(options)

    process.initialize_csv_file(out, data['pa_column_names'])

    for line in open(options.input):
        line = line.strip()
        if line == '' or line[0] == '#':
            continue

        chrom, pos, ref, alts, gene, csn, class_, cart = parsers.parse_VCF_record(line)

        for alt in alts:

            record = process.column_values(data, chrom, pos, ref, alt, gene, csn, class_)

            process.output_to_csv(out, chrom, pos, ref, alt, gene, csn, class_, cart, record)

    out.close()

    print '\nFinished.'
    print '='*100+'\n'


