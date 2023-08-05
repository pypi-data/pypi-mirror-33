import pytest
from   txtble import Txtble

# Taken from /usr/share/misc/birthtoken.gz in Ubuntu Xenial's miscfiles package:
HEADERS = ['Month', 'Birthstone', 'Birth Flower']
DATA = [
    ['January',   'Garnet',     'Carnation'],
    ['February',  'Amethyst',   'Violet'],
    ['March',     'Aquamarine', 'Jonquil'],
    ['April',     'Diamond',    'Sweetpea'],
    ['May',       'Emerald',    'Lily Of The Valley'],
    ['June',      'Pearl',      'Rose'],
    ['July',      'Ruby',       'Larkspur'],
    ['August',    'Peridot',    'Gladiolus'],
    ['September', 'Sapphire',   'Aster'],
    ['October',   'Opal',       'Calendula'],
    ['November',  'Topaz',      'Chrysanthemum'],
    ['December',  'Turquoise',  'Narcissus'],
]

TABLE = (
    '+---------+----------+------------------+\n'
    '|Month    |Birthstone|Birth Flower      |\n'
    '+---------+----------+------------------+\n'
    '|January  |Garnet    |Carnation         |\n'
    '|February |Amethyst  |Violet            |\n'
    '|March    |Aquamarine|Jonquil           |\n'
    '|April    |Diamond   |Sweetpea          |\n'
    '|May      |Emerald   |Lily Of The Valley|\n'
    '|June     |Pearl     |Rose              |\n'
    '|July     |Ruby      |Larkspur          |\n'
    '|August   |Peridot   |Gladiolus         |\n'
    '|September|Sapphire  |Aster             |\n'
    '|October  |Opal      |Calendula         |\n'
    '|November |Topaz     |Chrysanthemum     |\n'
    '|December |Turquoise |Narcissus         |\n'
    '+---------+----------+------------------+'
)

def test_one_expression():
    tbl = Txtble(DATA, headers=HEADERS)
    assert str(tbl) == TABLE

def test_append_each():
    tbl = Txtble(headers=HEADERS)
    for row in DATA:
        tbl.append(row)
    assert str(tbl) == TABLE

def test_extend_all():
    tbl = Txtble(headers=HEADERS)
    tbl.extend(DATA)
    assert str(tbl) == TABLE

def test_headers_attr():
    tbl = Txtble(DATA)
    tbl.headers = HEADERS
    assert str(tbl) == TABLE

def test_no_rstrip():
    tbl = Txtble(DATA, headers=HEADERS, rstrip=False)
    assert str(tbl) == TABLE

@pytest.mark.parametrize('header_border', [None, True, False])
def test_no_headers(header_border):
    tbl = Txtble(DATA, header_border=header_border)
    assert str(tbl) == (
        '+---------+----------+------------------+\n'
        '|January  |Garnet    |Carnation         |\n'
        '|February |Amethyst  |Violet            |\n'
        '|March    |Aquamarine|Jonquil           |\n'
        '|April    |Diamond   |Sweetpea          |\n'
        '|May      |Emerald   |Lily Of The Valley|\n'
        '|June     |Pearl     |Rose              |\n'
        '|July     |Ruby      |Larkspur          |\n'
        '|August   |Peridot   |Gladiolus         |\n'
        '|September|Sapphire  |Aster             |\n'
        '|October  |Opal      |Calendula         |\n'
        '|November |Topaz     |Chrysanthemum     |\n'
        '|December |Turquoise |Narcissus         |\n'
        '+---------+----------+------------------+'
    )

def test_embedded_newlines():
    tbl = Txtble(
        [
            ['Verse 1', 'Twas brillig, and the slithy toves\n'
                        'Did gyre and gimble in the wabe;\n'
                        'All mimsy were the borogoves,\n'
                        'And the mome raths outgrabe.'],
            ['Verse 2', '"Beware the Jabberwock, my son!\n'
                        'The jaws that bite, the claws that catch!\n'
                        'Beware the Jubjub bird, and shun\n'
                        'The frumious Bandersnatch!"'],
        ]
    )
    assert str(tbl) == (
        '+-------+-----------------------------------------+\n'
        '|Verse 1|Twas brillig, and the slithy toves       |\n'
        '|       |Did gyre and gimble in the wabe;         |\n'
        '|       |All mimsy were the borogoves,            |\n'
        '|       |And the mome raths outgrabe.             |\n'
        '|Verse 2|"Beware the Jabberwock, my son!          |\n'
        '|       |The jaws that bite, the claws that catch!|\n'
        '|       |Beware the Jubjub bird, and shun         |\n'
        '|       |The frumious Bandersnatch!"              |\n'
        '+-------+-----------------------------------------+'
    )

def test_embedded_trailing_newlines():
    tbl = Txtble(
        [
            ['Verse 1', 'Twas brillig, and the slithy toves\n'
                        'Did gyre and gimble in the wabe;\n'
                        'All mimsy were the borogoves,\n'
                        'And the mome raths outgrabe.\n'],
            ['Verse 2', '"Beware the Jabberwock, my son!\n'
                        'The jaws that bite, the claws that catch!\n'
                        'Beware the Jubjub bird, and shun\n'
                        'The frumious Bandersnatch!"\n'],
        ]
    )
    assert str(tbl) == (
        '+-------+-----------------------------------------+\n'
        '|Verse 1|Twas brillig, and the slithy toves       |\n'
        '|       |Did gyre and gimble in the wabe;         |\n'
        '|       |All mimsy were the borogoves,            |\n'
        '|       |And the mome raths outgrabe.             |\n'
        '|       |                                         |\n'
        '|Verse 2|"Beware the Jabberwock, my son!          |\n'
        '|       |The jaws that bite, the claws that catch!|\n'
        '|       |Beware the Jubjub bird, and shun         |\n'
        '|       |The frumious Bandersnatch!"              |\n'
        '|       |                                         |\n'
        '+-------+-----------------------------------------+'
    )

def test_embedded_trailing_newlines_no_border():
    tbl = Txtble(
        [
            ['Verse 1', 'Twas brillig, and the slithy toves\n'
                        'Did gyre and gimble in the wabe;\n'
                        'All mimsy were the borogoves,\n'
                        'And the mome raths outgrabe.\n'],
            ['Verse 2', '"Beware the Jabberwock, my son!\n'
                        'The jaws that bite, the claws that catch!\n'
                        'Beware the Jubjub bird, and shun\n'
                        'The frumious Bandersnatch!"\n'],
        ],
        border=False,
    )
    assert str(tbl) == (
        'Verse 1|Twas brillig, and the slithy toves\n'
        '       |Did gyre and gimble in the wabe;\n'
        '       |All mimsy were the borogoves,\n'
        '       |And the mome raths outgrabe.\n'
        '       |\n'
        'Verse 2|"Beware the Jabberwock, my son!\n'
        '       |The jaws that bite, the claws that catch!\n'
        '       |Beware the Jubjub bird, and shun\n'
        '       |The frumious Bandersnatch!"\n'
        '       |'
    )

def test_empty():
    tbl = Txtble()
    assert str(tbl) == '++\n++'

def test_empty_no_border():
    tbl = Txtble(border=False)
    assert str(tbl) == ''

def test_headers_no_rows():
    tbl = Txtble(headers=('This', 'That'))
    assert str(tbl) == (
        '+----+----+\n'
        '|This|That|\n'
        '+----+----+'
    )

def test_headers_empty_row():
    tbl = Txtble(headers=('This', 'That'), data=[[]])
    assert str(tbl) == (
        '+----+----+\n'
        '|This|That|\n'
        '+----+----+\n'
        '|    |    |\n'
        '+----+----+'
    )

def test_headers_blank_row():
    tbl = Txtble(headers=('This', 'That'), data=[['', '']])
    assert str(tbl) == (
        '+----+----+\n'
        '|This|That|\n'
        '+----+----+\n'
        '|    |    |\n'
        '+----+----+'
    )

def test_headers_no_rows_no_border():
    tbl = Txtble(headers=('This', 'That'), border=False)
    assert str(tbl) == 'This|That'

def test_tabs():
    tbl = Txtble(
        headers=['Head\ter'],
        data=[
            ['\t*'],
            ['*\t*'],
            ['*\t\t*'],
        ],
    )
    assert str(tbl) == (
        '+-----------------+\n'
        '|Head    er       |\n'
        '+-----------------+\n'
        '|        *        |\n'
        '|*       *        |\n'
        '|*               *|\n'
        '+-----------------+'
    )

def test_extra_whitespace():
    tbl = Txtble([
        ['  .leading.', '.trailing.  '],
        ['              ', 'inn   er'],
    ])
    assert str(tbl) == (
        '+--------------+------------+\n'
        '|  .leading.   |.trailing.  |\n'
        '|              |inn   er    |\n'
        '+--------------+------------+'
    )

def test_extra_whitespace_no_border():
    tbl = Txtble([
        ['  .leading.', '.trailing.  '],
        ['              ', 'inn   er'],
    ], border=False)
    assert str(tbl) == (
        '  .leading.   |.trailing.  \n'
        '              |inn   er'
    )

def test_empty_headers_no_header_fill():
    tbl = Txtble(DATA, headers=[])
    with pytest.raises(ValueError):
        str(tbl)

def test_empty_headers_header_fill():
    tbl = Txtble(DATA, headers=[], header_fill='Filler')
    assert str(tbl) == (
        '+---------+----------+------------------+\n'
        '|Filler   |Filler    |Filler            |\n'
        '+---------+----------+------------------+\n'
        '|January  |Garnet    |Carnation         |\n'
        '|February |Amethyst  |Violet            |\n'
        '|March    |Aquamarine|Jonquil           |\n'
        '|April    |Diamond   |Sweetpea          |\n'
        '|May      |Emerald   |Lily Of The Valley|\n'
        '|June     |Pearl     |Rose              |\n'
        '|July     |Ruby      |Larkspur          |\n'
        '|August   |Peridot   |Gladiolus         |\n'
        '|September|Sapphire  |Aster             |\n'
        '|October  |Opal      |Calendula         |\n'
        '|November |Topaz     |Chrysanthemum     |\n'
        '|December |Turquoise |Narcissus         |\n'
        '+---------+----------+------------------+'
    )

def test_headers_matching_columns():
    tbl = Txtble(DATA, headers=HEADERS, columns=len(HEADERS))
    assert str(tbl) == TABLE

@pytest.mark.parametrize('columns', [len(HEADERS)-1, len(HEADERS)+1])
def test_headers_not_matching_columns(columns):
    tbl = Txtble(DATA, headers=HEADERS, columns=columns)
    with pytest.raises(ValueError):
        str(tbl)
