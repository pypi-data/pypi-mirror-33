def main():
    with open('cliche_list.txt') as f:
        with open('cliche_list.py', 'w') as out:
            out.write('from typing import List\n\n')
            out.write('CLICHE_LINES: List[List[str]] = [\n')

            for line in f:
                out.write('    [')
                words = line.split()

                for idx, word in enumerate(words):
                    out.write('"%s"' % word.replace(',', ''))
                    if idx < (len(words) - 1):
                        out.write(", ")
                out.write('],\n')

            out.write(']\n')


if __name__ == '__main__':
    main()
