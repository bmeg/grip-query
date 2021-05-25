

def format_style(key):
    '''Dash formatting styles'''
    dictionary = {
        'font': 'Arial',
        'font_size_sm': 10,
        'font_size': 12,
        'font_size_lg': 14,
        'banner': {
            'textAlign': 'center',
            'color': '#026670',
            'type-font': 'Arial',
            'font-size': 50,
            'font-style': 'italic',
            'font-weight': 'bold',
            'padding': 10,
        },
        'subbanner': {
            'backgroundColor': '#88BDBC',
            'textAlign': 'center',
            'color': 'white',
            'type_font': 'Arial',
            'padding': 10,
        },
        'help_button': {
            'paddingTop': 2,
            'paddingBottom': 2,
            'paddingLeft': 8,
            'paddingRight': 8,
            'font-size': 10,
            'font-family': 'Arial',
        },
        'help_button_text': {
            'padding': 20,
            'font-size': 12,
            'font-family': 'Arial',
        },
    }
    return dictionary[key]
