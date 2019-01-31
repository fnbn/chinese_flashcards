import regex
import chardet

field_names = ['nummer', 'zeichen', 'striche',
               'bedeutung', 'aussprache', 'anmerkungen',
               'valenz', 'haeufigkeit', '214_radikale',
               'beispiele']

def read_in(file):
    with open(file, 'rb') as fp:
        encoding = chardet.detect(fp.read())
    with open(file, encoding=encoding['encoding']) as fp:
        lines = fp.read()
    return lines.split('\n')[0:-1]

def split_by_tab(lines):
    return [line.split('\t') for line in lines]

def split_examples(fields_set):
    def split_no_9(f):
        # split by chinese characters
        # splitting by unicode properties like script=han unfortunately not
        # possible in standard re library
        f[9] = regex.split('\P{script=han}(?=\\p{script=han})', f[9])
        # remove trailing commas
        f[9] = [x.rstrip(',') for x in f[9]]
        return f
    return [split_no_9(fields) for fields in fields_set]

def apply_translate_command(fields_set):
    command = '  \\translation{{{}}}{{{}}}{{{}}}'
    def apply_to_no_9(f):
        print(f[9])
        # split between '='
        f[9] = [field.split(' = ') for field in f[9]]
        # split first field between first character and rest
        def apply_to_no_1(f):
            return [f[0][0], f[0][1:], f[1]]
        f[9] = [apply_to_no_1(field) for field in f[9]]
        # remove leading space if present
        f[9] = [[field[0], field[1].lstrip(' '), field[2]] for field in f[9]]
        # format
        f[9] = ',\n'.join([command.format(*field) for field in f[9]])
        return f
    return [apply_to_no_9(fields) for fields in fields_set]

def strip_surrounding_spaces(fields_set):
    return [[f.lstrip(' ').rstrip(' ') for f in field] for field in fields_set]

def apply_overall_command(fields_set):
    command = "\\renewcommand{{\\flfoot}}{{\\scriptsize {striche} Strich{plural} / {haeufigkeit}}}\n"
    command = command + "\\card{{{zeichen}}}{{\n"
    command = command + "  \\translation{{}}{{{aussprache}}}{{{bedeutung}}}\\\\[1em]\n"
    command = command + "  {beispiele}\n"
    command = command + "}}\n"
    return [command.format(striche=fields[2],
                           plural='e' if int(fields[2]) > 1 else '',
                           haeufigkeit=fields[7],
                           zeichen=fields[1],
                           aussprache=fields[4],
                           bedeutung=fields[3],
                           beispiele=fields[9]) for fields in fields_set]

if __name__ == '__main__':
    lines = read_in('radicals.csv')
    fields_set = split_by_tab(lines)
    fields_set = split_examples(fields_set)
    fields_set = apply_translate_command(fields_set)
    fields_set = strip_surrounding_spaces(fields_set)
    commands = apply_overall_command(fields_set)
    print('\n'.join(commands))

