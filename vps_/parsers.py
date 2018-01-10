from collections import OrderedDict
import sys


def read_data(options):

    ret = {}
    sys.stdout.write('Reading data from files ... ')
    sys.stdout.flush()
    ret.update(read_variant_data_files(options))
    ret.update(parse_pa_files(options.palist))
    ret['gene_config_data'] = parse_gene_config_file(options.geneconfig)
    print 'done'
    return ret


def read_variant_data_files(options):

    ret = {}

    ret['maxentscan_data'] = parse_variant_data_file(
        options.maxentscan,
        header=[
            'CHROM', 'POS', 'REF', 'ALT', 'ENST', 'GENE', 'LOC', 'CSN', 'CLASS', 'RefKnown5', 'RefKnown3',
            'AltKnown', 'AltHighest5', 'RefHighest5', 'AltHighest3', 'RefHighest3', 'Boundary5', 'Boundary3'
        ]
    )

    ret['google_search_data'] = parse_variant_data_file(
        options.gs,
        header=['Gene', 'CSN', 'google_search']
    )

    ret['exac_data'] = parse_variant_data_file(
        options.exac,
        header=['CHROM', 'POS', 'REF', 'ALT']
    )

    ret['gnomad_exomes_data'] = parse_variant_data_file(
        options.gnomadex,
        header=['CHROM', 'POS', 'REF', 'ALT']
    )

    ret['gnomad_genomes_data'] = parse_variant_data_file(
        options.gnomadgen,
        header=['CHROM', 'POS', 'REF', 'ALT']
    )

    ret['curation_data'] = parse_variant_data_file(
        options.curation,
        header=['Gene', 'CSN', 'Curation', 'CurationDate']
    )

    ret['common_data'] = parse_variant_data_file(
        options.common,
        header=['Gene', 'CSN']
    )

    return ret


def parse_variant_data_file(fn, header=None):

    ret = {}
    for line in open(fn):
        line = line.strip()
        if line == '':
            continue
        cols = line.split('\t')

        if line.split()[0].upper() in ['CHROM', 'GENE']:
            if header is None:
                header = cols
            continue

        value = OrderedDict()
        for i in range(len(header)):
            value[header[i]] = cols[i] if len(cols)-1 >= i else '.'

        key = '_'.join(cols[:4]) if header[0].upper() == 'CHROM' else '_'.join(cols[:2])
        ret[key] = value

    return ret


def parse_pa_files(fn):

    ret = {}

    pa_data = {}
    pa_column_names = []

    pa_files = []
    for line in open(fn):
        line = line.strip()
        pa_files.append(line)

    for pa_file in pa_files:
        with open(pa_file, 'r') as f:
            header_line = f.readline().strip()
            pa_column_names += header_line.split('\t')[4:]

        data = parse_variant_data_file(pa_file)

        for key, values in data.iteritems():
            if key not in pa_data:
                pa_data[key] = {}
            pa_data[key].update(values)

    ret['pa_data'] = pa_data
    ret['pa_column_names'] = pa_column_names

    return ret


def parse_gene_config_file(fn):

    ret = {}
    for line in open(fn):
        line = line.strip()
        if line == '' or line[0] == '#':
            continue
        cols = line.split()
        if cols[2] == 'cDNAStart':
            continue

        if cols[0] not in ret:
            ret[cols[0]] = []

        cdna_starts, cdna_ends = cols[2].split(','), cols[3].split(',')
        for i in range(len(cdna_starts)):
            ret[cols[0]].append(
                {
                    'RegionType': cols[1],
                    'cDNAStart': cdna_starts[i],
                    'cDNAEnd': cdna_ends[i],
                    'CategoryType': cols[4]
                }
            )
    return ret


def parse_VCF_record(record):

    cols = record.split('\t')
    chrom = cols[0]
    pos = cols[1]
    ref = cols[3]
    alts = cols[4].split(',')
    info = cols[7]

    info_flags = {}
    for x in info.split(';'):
        [k,v] = x.split('=', 1)
        info_flags[k] = v
    gene = info_flags.get('GENE')
    csn = info_flags.get('CSN')
    class_ = info_flags.get('CLASS')
    cart = info_flags.get('TRANSCRIPT')

    return chrom, pos, ref, alts, gene, csn, class_, cart
