def show_text(screen, font, str, place, color=(255, 255, 255)):
    rtext = font.render(str, True, color)
    screen.blit(rtext, place)

def long_text(screen, max_width, font, str, place, color=(255, 255, 255), only_return=False, ignore_chars=0):

    if font.size(str)[0] <= max_width:
        if not only_return:
            show_text(screen, font, str, place, color)
        return str

    if ignore_chars == 0:
        check_str = ''
        words = str.split()
        for word in words:
            prevlen = len(check_str)
            if prevlen > 0:
                check_str += ' '
            check_str += word
            if font.size(check_str)[0] > max_width:
                ignore_chars = prevlen

    for i in range(ignore_chars + 1, len(str)):
        if font.size(str[:i])[0] > max_width:
            for j in range(i, 0, -1):
                if font.size(str[:j] + '...')[0] <= max_width:
                    if not only_return:
                        show_text(screen, font, str[:j] + '...', place, color)
                    return str[:j] + '...'

    if not only_return:
        show_text(screen, font, str, place, color)
    return str

def multiline_text(screen, max_lines, height_change, max_width, font, str, place, color=(255, 255, 255), only_return = False):
    lines = ['']
    words = str.split()
    too_long = False

    for word in words:

        if len(lines[len(lines) - 1]) > 0:
            modified_line = lines[len(lines) - 1] + ' ' + word
        else:
            modified_line = lines[len(lines) - 1] + word

        if font.size(modified_line)[0] <= max_width:
            lines[len(lines) - 1] = modified_line
        elif len(lines) < max_lines:
            if font.size(word)[0] <= max_width:
                lines.append(word)
            else:
                lines.append(long_text(screen, max_width, font, words[i], place, color, True))
                if len(lines) < max_lines:
                    lines.append('')
        else:
            lines[max_lines - 1] = long_text(screen, max_width, font, modified_line, place, color, True, len(lines[max_lines - 1]))
            too_long = True

    if not only_return:
        for i in range(len(lines)):
            show_text(screen, font, lines[i], (place[0], place[1] + height_change * i), color)
    
    return too_long