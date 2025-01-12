def show_text(screen, font, s, place, color=(255, 255, 255)):
    rtext = font.render(s, True, color)
    screen.blit(rtext, place)

def long_text(screen, max_width, font, s, place, color=(255, 255, 255), only_return=False, ignore_chars=0):
    if font.size(s)[0] <= max_width:
        if not only_return:
            show_text(screen, font, s, place, color)
        return s

    if ignore_chars == 0:
        check_str = ''
        words = s.split(' ')
        for word in words:
            prevlen = len(check_str)
            if prevlen > 0:
                check_str += ' '
            check_str += word
            if font.size(check_str)[0] > max_width:
                ignore_chars = prevlen
                break

    for i in range(ignore_chars + 1, len(s) + 1):
        if font.size(s[:i])[0] > max_width:
            for j in range(i, 1, -1):
                if font.size(s[:j] + '...')[0] <= max_width:
                    if not only_return:
                        show_text(screen, font, s[:j] + '...', place, color)
                    return s[:j] + '...'
            if font.size(s[0])[0] <= max_width:
                s = s[0]
            else:
                s = ''
            break
    if not only_return:
        show_text(screen, font, s, place, color)
    return s

def multiline_text(screen, max_lines, height_change, max_width, font, s, place, color=(255, 255, 255), only_return = False):
    lines = ['']
    words = s.split(' ')
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
                if len(lines) == 1 and len(lines[0]) == 0:
                    lines.pop(0)
                lines.append(long_text(screen, max_width, font, word, place, color, True))
                if len(lines) < max_lines:
                    lines.append('')
                else:
                    too_long = True
        else:
            lines[max_lines - 1] = long_text(screen, max_width, font, modified_line, place, color, True, len(lines[max_lines - 1]))
            too_long = True

        if too_long: break

    if not only_return:
        for i in range(len(lines)):
            show_text(screen, font, lines[i], (place[0], place[1] + height_change * i), color)
    
    return too_long