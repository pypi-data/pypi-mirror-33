from clean.infra.log.utils.colors.termcolors import (
    DARK_PALETTE, DEFAULT_PALETTE, LIGHT_PALETTE, NOCOLOR_PALETTE, PALETTES,
    colorize, parse_color_setting,
)


def test_empty_string():
    assert parse_color_setting('') == PALETTES[DEFAULT_PALETTE]


def test_simple_palette():
    assert parse_color_setting('light') == PALETTES[LIGHT_PALETTE]
    assert parse_color_setting('dark') == PALETTES[DARK_PALETTE]
    assert parse_color_setting('nocolor') is None


def test_fg():
    res = parse_color_setting('error=green')

    assert res == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'})


def test_fg_bg():
    res = parse_color_setting('error=green/blue')
    assert res == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'bg': 'blue'})


def test_fg_opts():
    res_green_blink = parse_color_setting('error=green,blink')
    res_green_bold_blink = parse_color_setting('error=green,bold,blink')

    assert res_green_blink == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'opts': ('blink',)})
    assert res_green_bold_blink == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'opts': ('blink', 'bold')})


def test_fg_bg_opts():
    res_blue_blink = parse_color_setting('error=green/blue,blink')
    res_blu_bold_blink = parse_color_setting('error=green/blue,bold,blink')

    assert res_blue_blink == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'bg': 'blue', 'opts': ('blink',)})
    assert res_blu_bold_blink == dict(PALETTES[NOCOLOR_PALETTE],
                                      ERROR={'fg': 'green', 'bg': 'blue', 'opts': ('blink', 'bold')})


def test_override_palette():
    res = parse_color_setting('light;error=green')

    assert res == dict(PALETTES[LIGHT_PALETTE], ERROR={'fg': 'green'})


def test_override_nocolor():
    res = parse_color_setting('nocolor;error=green')

    assert res == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'})


def test_reverse_override():
    assert parse_color_setting('error=green;light') == PALETTES[LIGHT_PALETTE]


def test_multiple_roles():
    res = parse_color_setting('error=green;sql_field=blue')

    assert res == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'}, SQL_FIELD={'fg': 'blue'})


def test_override_with_multiple_roles():
    res = parse_color_setting('light;error=green;sql_field=blue')

    assert res == dict(PALETTES[LIGHT_PALETTE], ERROR={'fg': 'green'}, SQL_FIELD={'fg': 'blue'})


def test_empty_definition():
    assert parse_color_setting(';') is None
    assert parse_color_setting(';;;') is None
    assert parse_color_setting('light;') == PALETTES[LIGHT_PALETTE]


def test_empty_options():
    res_1 = parse_color_setting('error=green,')
    res_2 = parse_color_setting('error=green,,,')
    res_3 = parse_color_setting('error=green,,blink,,')

    assert res_1 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'})
    assert res_2 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'})
    assert res_3 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'opts': ('blink',)})


def test_bad_palette():
    assert parse_color_setting('unknown') is None


def test_bad_role():
    res_1 = parse_color_setting('unknown=green;sql_field=blue')

    assert res_1 == dict(PALETTES[NOCOLOR_PALETTE], SQL_FIELD={'fg': 'blue'})
    assert parse_color_setting('unknown=') is None
    assert parse_color_setting('unknown=green') is None


def test_bad_color():
    res_1 = parse_color_setting('error=;sql_field=blue')
    res_2 = parse_color_setting('error=unknown;sql_field=blue')
    res_3 = parse_color_setting('error=green/unknown')
    res_4 = parse_color_setting('error=green/blue/something')
    res_5 = parse_color_setting('error=green/blue/something,blink')

    assert res_1 == dict(PALETTES[NOCOLOR_PALETTE], SQL_FIELD={'fg': 'blue'})
    assert res_2 == dict(PALETTES[NOCOLOR_PALETTE], SQL_FIELD={'fg': 'blue'})
    assert res_3 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'})
    assert res_4 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'bg': 'blue'})
    assert res_5 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'bg': 'blue', 'opts': ('blink',)})
    assert parse_color_setting('error=') is None
    assert parse_color_setting('error=unknown') is None


def test_bad_option():
    res_1 = parse_color_setting('error=green,unknown')
    res_2 = parse_color_setting('error=green,unknown,blink')

    assert res_1 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'})
    assert res_2 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'opts': ('blink',)})


def test_role_case():
    res_1 = parse_color_setting('ERROR=green')
    res_2 = parse_color_setting('eRrOr=green')

    assert res_1 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'})
    assert res_2 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'})


def test_color_case():
    res_1 = parse_color_setting('error=GREEN')
    res_2 = parse_color_setting('error=GREEN/BLUE')
    res_3 = parse_color_setting('error=gReEn')
    res_4 = parse_color_setting('error=gReEn/bLuE')

    assert res_1 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'})
    assert res_2 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'bg': 'blue'})
    assert res_3 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green'})
    assert res_4 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'bg': 'blue'})


def test_opts_case():
    res_1 = parse_color_setting('error=green,BLINK')
    res_2 = parse_color_setting('error=green,bLiNk')

    assert res_1 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'opts': ('blink',)})
    assert res_2 == dict(PALETTES[NOCOLOR_PALETTE], ERROR={'fg': 'green', 'opts': ('blink',)})


def test_colorize_empty_text():
    res_1 = colorize(text=None)
    res_2 = colorize(text='')
    res_3 = colorize(text=None, opts=('noreset', ))
    res_4 = colorize(text='', opts=('noreset', ))

    assert res_1 == '\x1b[m\x1b[0m'
    assert res_2 == '\x1b[m\x1b[0m'
    assert res_3 == '\x1b[m'
    assert res_4 == '\x1b[m'
