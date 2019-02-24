def select_county():
    ret = ''
    for entry in select name from city:
        ret += '<option value="{}">{}</option>'.format(entry)
    return ret
