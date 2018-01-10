import helper


###################################################################################################################
# Writing to CSV file
###################################################################################################################

def initialize_csv_file(out, pa_column_names):

    header = [
        'CHROM',
        'POS',
        'REF',
        'ALT',
        'GENE',
        'CSN',
        'CLASS',
        'CART_ID',
        'GeneSpecificPTVFlag',
        'InSilicoPTVCategory',
        'MAX5',
        'PI5',
        'MAX3',
        'PI3',
        'SpliceSiteScore',
        'PercentReduction',
        'SpliceSiteType',
        'GeneSpecificSplicingFlag',
        'InSilicoSplicingCategory'
    ]
    header += pa_column_names
    header += [
        'GeneSpecificPAFlag',
        'InSilicoPACategory',
        'AutomatedColour',
        'GSLink',
        'ExACLink',
        'gnomADLink'
        'Curation',
        'CurationDate'
    ]

    out.write('\t'.join(header)+'\n')


def output_to_csv(out, chrom, pos, ref, alt, gene, csn, class_, cart, record):

    r = [
        chrom,
        pos,
        ref,
        alt,
        helper.make_excel_text(gene),
        csn,
        class_,
        cart,
        record['GeneSpecificPTVFlag'],
        record['InSilicoPTVCategory'],
        record['MAX5'],
        record['PI5'],
        record['MAX3'],
        record['PI3'],
        record['SpliceSiteScore'],
        record['PercentReduction'],
        record['SpliceSiteType'],
        record['GeneSpecificSplicingFlag'],
        record['InSilicoSplicingCategory']
    ]
    r += record['pa_values']
    r += [
        record['GeneSpecificPAFlag'],
        record['InSilicoPACategory'],
        record['AutomatedColour'],
        helper.make_excel_link_str(record['GSLink'], 'GS'),
        helper.make_excel_link_str(record['ExACLink'], 'ExAC'),
        helper.make_excel_link_str(record['gnomADLink'], 'gnomAD'),
        record['Curation'],
        record['CurationDate']
    ]

    r = map(helper.float_digits, r)
    r = map(str, r)

    out.write('\t'.join(r) + '\n')



###################################################################################################################
# Calculating column values
###################################################################################################################


def column_values(data, chrom, pos, ref, alt, gene, csn, class_):

    ret = {}
    key = '_'.join([chrom, pos, ref, alt])

    if key not in data['maxentscan_data']:
        # Must handle this case
        pass

    # PI5, PI3, SpliceSiteScore, SpliceSiteType, PercentReduction, MAX5, MAX3
    ret = maxentscan_values(ref, alt, key, data['maxentscan_data'], ret)

    # PA values
    ret['pa_values'] = process_pa_data(data['pa_data'], data['pa_column_names'], key)

    # GeneSpecificPAFlag, GeneSpecificPTVFlag, GeneSpecificSplicingFlag
    ret = gene_specific_flags(data['pa_data'], data['gene_config_data'], gene, class_, csn, key, ret)

    # InSilicoPACategory, InSilicoPTVCategory, InSilicoSplicingCategory
    ret = in_silico_categories(ret, data['maxentscan_data'], key)

    # GSLink
    ret['GSLink'] = google_search(data['google_search_data'], gene, csn)

    # Broad links
    ret.update(broad_links(data['exac_data'], data['gnomad_exomes_data'], data['gnomad_genomes_data'], key))

    # Curation
    ret.update(curation(data['curation_data'], gene, csn))

    # AutomatedColour
    ret['AutomatedColour'] = automated_colour(data['common_data'], gene, csn, ret, class_)

    return ret


# Helper functions for calculating column values

def maxentscan_values(ref, alt, key, maxentscan_data, values):

    if len(ref) == 1 and len(alt) == 1:
        values['PI5'] = pi5(maxentscan_data, key)
        values['PI3'] = pi3(maxentscan_data, key)
        values.update(process_maxentscan_data(maxentscan_data, key))
    else:
        for x in ['PI5', 'PI3', 'RefKnown', 'SpliceSiteScore', 'SpliceSiteType', 'PercentReduction', 'MAX5', 'MAX3']:
            values[x] = 'review'
    return values


def gene_specific_flags(pa_data, gene_config_data, gene, class_, csn, key, values):

    if key not in pa_data or class_ == 'IM':
        values['GeneSpecificPAFlag'] = '.'
    else:
        values['GeneSpecificPAFlag'] = gene_specific_pa_flag(gene_config_data, gene, class_, csn)
    values['GeneSpecificPTVFlag'] = gene_specific_ptv_flag(gene_config_data, gene, class_, csn)
    values['GeneSpecificSplicingFlag'] = gene_specific_splicing_flag(gene_config_data, gene, class_, csn)
    return values


def in_silico_categories(values, maxentscan_data, key):

    values['InSilicoPACategory'] = in_silico_pa_category(values['GeneSpecificPAFlag'], values['pa_values'])
    values['InSilicoPTVCategory'] = in_silico_ptv_category(values['GeneSpecificPTVFlag'])
    values['InSilicoSplicingCategory'] = in_silico_splicing_category(values, maxentscan_data[key])
    return values


def process_pa_data(pa_data, pa_column_names, key):

    if key not in pa_data:
        return ['.']*len(pa_column_names)

    ret = []
    for c in pa_column_names:
        value = pa_data[key].get(c)
        if value is None:
            value = '.'
        ret.append(value)
    return ret


def google_search(google_search_data, gene, csn):

    return google_search_data[gene+'_'+csn]['google_search'] if gene+'_'+csn in google_search_data else '.'


def broad_links(exac_data, gnomad_exomes_data, gnomad_genomes_data, key):

    ret = {'ExACLink': '.', 'gnomADLink': '.'}

    if key in exac_data:
        ret['ExACLink'] = 'http://exac.broadinstitute.org/variant/' + '-'.join(key.split('_'))

    if key in gnomad_exomes_data or key in gnomad_genomes_data:
        ret['gnomADLink'] = 'http://gnomad.broadinstitute.org/variant/' + '-'.join(key.split('_'))

    return ret


def curation(curation_data, gene, csn):

    ret = {'Curation': '.', 'CurationDate': '.'}
    if gene+'_'+csn in curation_data:
        ret['Curation'] = curation_data[gene+'_'+csn]['Curation']
        ret['CurationDate'] = curation_data[gene+'_'+csn]['CurationDate']

    return ret


def automated_colour(common_data, gene, csn, values, class_):

    if class_ in ['IM', 'SL', 'IF']:
        return 'grey'

    if gene+'_'+csn in common_data:
        if values['InSilicoPTVCategory'] != '.' and values['InSilicoSplicingCategory'] in ['review', '4']:
            return 'grey'
        else:
            return 'blue'

    if values['InSilicoPTVCategory'] in ['.', '2'] and values['InSilicoSplicingCategory'] == '2' and values['InSilicoPACategory'] in ['.', '2']:
        return 'blue'

    if values['InSilicoPTVCategory'] == '.' and values['InSilicoSplicingCategory'] == '2' and values['InSilicoPACategory'] == 'review':
        return 'grey'

    if values['InSilicoPTVCategory'] == 'review':
        return 'grey'

    if values['InSilicoPTVCategory'] == '.' and values['InSilicoSplicingCategory'] == 'review':
        return 'grey'

    if values['InSilicoPTVCategory'] == '2' and values['InSilicoSplicingCategory'] in ['review', '4']:
        return 'grey'

    if values['InSilicoPTVCategory'] in ['.', '4'] and values['InSilicoSplicingCategory'] == '4':
        return 'red'

    if values['InSilicoPTVCategory'] == '4' and values['InSilicoSplicingCategory'] == '2':
        return 'red'

    if values['InSilicoPTVCategory'] == '4' and values['InSilicoSplicingCategory'] == 'review':
        if class_ == 'SG':
            return 'red'
        if class_ == 'ESS':
            return 'grey'

    return 'pending'


# Helper functions for processing MaxEntScan data

def pi5(maxentscan_data, key):

    d = maxentscan_data[key]

    Alt5 = '.' if d['AltKnown'] != '.' else d['AltHighest5']

    if Alt5 == '.':
        return '.'

    AltHighest5 = float(d['AltHighest5'])
    RefHighest5 = float(d['RefHighest5'])

    if AltHighest5 <= 0:
        return 0
    if RefHighest5 <= 0:
        return 100

    tmp = int(round(100 * (AltHighest5 - min(RefHighest5, AltHighest5)) / RefHighest5))
    return min(100, tmp)


def pi3(maxentscan_data, key):

    d = maxentscan_data[key]

    Alt3 = '.' if d['AltKnown'] != '.' else d['AltHighest3']

    if Alt3 == '.':
        return '.'

    AltHighest3 = float(d['AltHighest3'])
    RefHighest3 = float(d['RefHighest3'])

    if AltHighest3 <= 0:
        return 0
    if RefHighest3 <= 0:
        return 100

    tmp = int(round(100 * (AltHighest3 - min(RefHighest3, AltHighest3)) / RefHighest3))
    return min(100, tmp)


def ref_known(maxentscan_data, key):

    d = maxentscan_data[key]

    if d['AltKnown'] == '.':
        return '.'

    if '+' in d['CSN']:
        return d['RefKnown5']

    if '-' in d['CSN']:
        return d['RefKnown3']

    cval = int(d['CSN'][2:d['CSN'].find('>') - 1])
    if int(d['Boundary5']) - 2 <= cval <= int(d['Boundary5']):
        return d['RefKnown5']
    else:
        if int(d['Boundary3']) <= cval <= int(d['Boundary3']) + 2:
            return d['RefKnown3']
        else:
            return 'check'


def percent_reduction(maxentscan_data, ref_known, key):

    d = maxentscan_data[key]

    if d['AltKnown'] == '.':
        return '.'

    y = float(ref_known)

    if float(d['AltKnown']) < 0:
        z = 0
    else:
        if float(d['AltKnown']) > float(ref_known):
            z = float(ref_known)
        else:
            z = float(d['AltKnown'])

    x = float(ref_known) - z

    return round(100 * x / y, 2)


def process_maxentscan_data(maxentscan_data, key):

    ret = {}
    ret['RefKnown'] = ref_known(maxentscan_data, key)
    ret['SpliceSiteScore'] = ret['RefKnown']
    ret['SpliceSiteType'] = 'spliceSiteRegion' if ret['SpliceSiteScore'] != '.' else '.'
    ret['PercentReduction'] = percent_reduction(maxentscan_data, ret['RefKnown'], key)
    d = maxentscan_data[key]
    ret['MAX5'] = d['AltHighest5']
    ret['MAX3'] = d['AltHighest3']
    return ret


# Helper functions for calculating gene specific flags

def gene_specific_ptv_flag(gene_config_data, gene, class_, csn):

    if class_ not in ['ESS', 'SG', 'FS']:
        return '.'
    return proccess_overlap(gene_config_data, gene, csn, 'PTV')


def gene_specific_splicing_flag(gene_config_data, gene, class_, csn):

    if class_ == 'IM':
        return 'no'
    return proccess_overlap(gene_config_data, gene, csn, 'Splicing')


def gene_specific_pa_flag(gene_config_data, gene, class_, csn):

    if class_ != 'NSY':
        return 'no'
    return proccess_overlap(gene_config_data, gene, csn, 'NSY')


def proccess_overlap(gene_config_data, gene, csn, region_type):

    overlap = False
    if gene in gene_config_data:
        for d in gene_config_data[gene]:
            if d['RegionType'] != region_type:
                continue
            if csn_overlaps_with_region(csn, d):
                overlap = True
                if d['CategoryType'] == 'review':
                    return 'review'
    return 'yes' if overlap else 'no'


def csn_overlaps_with_region(csn, region_def):

    region = helper.Region(region_def['cDNAStart'], region_def['cDNAEnd'])
    coord_part1, coord_part2, dna_change = helper.parse_csn(csn)

    if dna_change.startswith('ins'):
        region_endpoint1 = helper.Region(coord_part1, coord_part1)
        region_endpoint2 = helper.Region(coord_part2, coord_part2)
        return region.overlaps(region_endpoint1) and region.overlaps(region_endpoint2)

    elif dna_change.startswith('dup'):
        if coord_part2 is None:
            region_variant = helper.Region(coord_part1, helper.increase_csn_coordinate(coord_part1))
        else:
            region_variant = helper.Region(coord_part2, helper.increase_csn_coordinate(coord_part2))
        return region.overlaps(region_variant)

    else:
        region_variant = helper.Region(coord_part1, coord_part1) if coord_part2 is None else helper.Region(coord_part1, coord_part2)
        return region.overlaps(region_variant)


# Helper functions for calculating in silico categories

def in_silico_pa_category(gene_specific_pa_flag, pa_values):

    if gene_specific_pa_flag == 'review':
        return 'review'
    else:
        if gene_specific_pa_flag == 'no':
            return '2'
        else:
            if pa_values[0] == '0':
                return 'review'
            else:
                if pa_values[1] == 'Class C65':
                    return 'review'
                else:
                    return '.' if pa_values[0] == '.' else '2'


def in_silico_ptv_category(gene_specific_ptv_flag):

    if gene_specific_ptv_flag == 'review':
        return 'review'
    else:
        if gene_specific_ptv_flag == 'yes':
            return '4'
        else:
            return '.' if gene_specific_ptv_flag == '.' else '2'


def in_silico_splicing_category(values, maxentscan_data):

    if values['GeneSpecificSplicingFlag'] == 'review':
        return 'review'

    if values['GeneSpecificSplicingFlag'] == 'no':
        return '2'

    if maxentscan_data['AltKnown'] != '.':
        return '4' if values['PercentReduction'] >= 50 and values['SpliceSiteScore'] >= 2 else 'review'
    else:
        Alt5 = float(maxentscan_data['AltHighest5'])
        Alt3 = float(maxentscan_data['AltHighest3'])

        if Alt5 >= 4 or Alt3 >= 4:
            return 'review' if (values['PI5'] >= 50 and Alt5 >= 4) | (values['PI3'] >= 50 and Alt3 >= 4) else '2'
        else:
            return '2'
