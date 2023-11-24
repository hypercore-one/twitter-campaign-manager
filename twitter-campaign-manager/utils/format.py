def sanitize_output(text):
    escape_chars = ['!', '-', '#', '.', '>', '=', '(', ')', '[', ']', '|', '@', '_', '+', '{', '}']
    for c in escape_chars:
        text = text.replace(c, f'\\{c}')
    return text


def format_post_criteria(arr):
    if len(arr) == 1:
        return arr[0].replace("'", '')

    response = ''
    for tag in arr:
        response += '{}, '.format(tag.replace("'", ''))
    return response[:-2]
