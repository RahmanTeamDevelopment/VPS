
class Coordinate(object):

    def __init__(self, as_str):

        self.as_str = as_str


    def split(self, s):

        if '+' in s:
            [x, y] = s.split('+')
            return int(x), int(y)
        if '-' in s:
            [x, y] = s.split('-')
            return int(x), -int(y)
        return int(s), 0


    def compare_coordinates_both_minus(self, x, y):
        x = x[1:]
        y = y[1:]

        x_e, x_i = self.split(x)
        y_e, y_i = self.split(y)

        if x_e != y_e:
            if x_e < y_e:
                return 1
            else:
                return -1
        else:
            if x_i > y_i:
                return 1
            else:
                return -1


    def __cmp__(self, other):

        x = self.as_str
        y = other.as_str

        if x.upper() == 'END':
            return 1

        if y.upper() == 'END':
            return -1

        if x == y:
            return 0

        if x[0] == '+' and y[0] != '+':
            return 1
        elif x[0] != '+' and y[0] == '+':
            return -1
        elif x[0] == '+' and y[0] == '+':
            x = x[1:]
            y = y[1:]

        if x[0] == '-' and y[0] != '-':
            return -1
        elif x[0] != '-' and y[0] == '-':
            return 1
        elif x[0] == '-' and y[0] == '-':
            return self.compare_coordinates_both_minus(x, y)

        x_e, x_i = self.split(x)
        y_e, y_i = self.split(y)

        if x_e != y_e:
            if x_e > y_e:
                return 1
            else:
                return -1
        else:
            if x_i > y_i:
                return 1
            else:
                return -1


    def __str__(self):

        return self.as_str


class Region(object):

    def __init__(self, start, end):

        self.start = Coordinate(start)
        self.end = Coordinate(end)


    def overlaps(self, other):

        return self.start <= other.start <= self.end or other.start <= self.start <= other.end


#######################################################################################################################


def parse_csn(csn):

    # Split to ger c. part
    csn_c = csn.split('_p.', 1)[0] if '_p.' in csn else csn

    # Find where to split the c. part to get coordinates and dna change
    found = [csn_c.find(x) for x in ['A>', 'C>', 'G>', 'T>', 'del', 'ins', 'dup'] if x in csn_c]
    cuthere = min(found)

    # Split c. part to get coordinates and dna change
    coords = csn_c[csn_c.find("c.") + 2:cuthere]
    dna_change = csn_c[cuthere:]

    # Split coordinates to first and second coordinate
    if "_" in coords:
        [coord_part1, coord_part2] = coords.split('_', 1)
    else:
        coord_part1, coord_part2 = coords, None

    return coord_part1, coord_part2, dna_change


def increase_csn_coordinate(c):

    if '+' in c:
        idx = c.rfind('+')
        x = c[:idx]
        y = c[idx+1:]
        return '{}+{}'.format(x, int(y) + 1)
    elif '-' in c:
        idx = c.rfind('-')
        x = c[:idx]
        y = c[idx + 1:]
        ynew = int(y) - 1
        if ynew == 0:
            return str(x)
        return '{}-{}'.format(x, ynew)
    else:
        return str(int(c) + 1)


def float_digits(x):

    if type(x) == float:
        w = str("%.2f" % x)
        if '.' not in w:
            return w
        while w[-1] == '0':
            w = w[:-1]
        if w[-1] == '.':
            w = w[:-1]
        return w
    else:
        return x


def make_excel_link_str(link, text):

    if link == '.':
        return '.'
    return '=HYPERLINK(\"{}\",\"{}\")'.format(link, text)


def make_excel_text(text):

    return '=\"{}\"'.format(text)


def exon_endpoints(data):

    ret_start = {}
    ret_end = {}

    for k,v in data.iteritems():

        if v['CLASS'] == 'ESS':
            x = v['CSN']
            x = x[:x.find('_')]

            if '-' in x:
                idx = x.find('-')
                endpoint = int(x[2:idx])
                if v['GENE'] not in ret_start:
                    ret_start[v['GENE']] = []
                if endpoint not in ret_start[v['GENE']]:
                    ret_start[v['GENE']].append(endpoint)
            else:
                idx = x.find('+')
                endpoint = int(x[2:idx])
                if v['GENE'] not in ret_end:
                    ret_end[v['GENE']] = []
                if endpoint not in ret_end[v['GENE']]:
                    ret_end[v['GENE']].append(endpoint)

    return ret_start, ret_end


def add_ee_positions(gene_config_data, endpoints_start_data, endpoints_end_data):

    new = {}

    for gene, values_list in gene_config_data.iteritems():

        tmp = []

        for values in values_list:
            if values['CategoryType'] != 'review':
                continue
            start, _ = split_coordinate(values['cDNAStart'])
            end, _ = split_coordinate(values['cDNAEnd'])

            if gene in endpoints_start_data:
                if start in endpoints_start_data[gene]:
                    tmp.append(
                        {
                            'RegionType': values['RegionType'],
                            'cDNAStart': str(start),
                            'cDNAEnd': str(start+2),
                            'CategoryType': 'review'
                        }
                    )

            if gene in endpoints_end_data:
                if end in endpoints_end_data[gene]:
                    tmp.append(
                        {
                            'RegionType': values['RegionType'],
                            'cDNAStart': str(end-1),
                            'cDNAEnd': str(end),
                            'CategoryType': 'review'
                        }
                    )

        if len(tmp) > 0:
            new[gene] = tmp

    for gene, v in new.iteritems():
        gene_config_data[gene] += v

    return gene_config_data


def split_coordinate(s):

    if '+' in s:
        [x, y] = s.split('+')
        return int(x), int(y)
    if '-' in s:
        [x, y] = s.split('-')
        return int(x), -int(y)
    return int(s), 0
