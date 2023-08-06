def get_min_max_bracket_values(brackets):
    """
    # extract bracket values from index
    :param brackets:
    :return:
    """
    min_max_brackets = []
    for bracket in brackets.index:
        dollar_sign_position = [dpos for dpos, cval in enumerate(bracket) if cval == '$']
        if dollar_sign_position[0] == 0 and len(dollar_sign_position) == 1:
            minimum = ''.join([val for val in bracket if str.isdigit(val)])
            min_max_brackets.append([int(minimum), int(int(minimum)+int(minimum)/4)])
        elif dollar_sign_position[0] != 0 and len(dollar_sign_position) == 1:
            maximum = ''.join([val for val in bracket if str.isdigit(val)])
            min_max_brackets.append([0, int(maximum)])
        else:
            minimum = ''.join([val for val in bracket[:dollar_sign_position[1]] if str.isdigit(val)])
            maximum = ''.join([val for val in bracket[dollar_sign_position[1]:] if str.isdigit(val)])
            min_max_brackets.append([int(minimum), int(maximum)])
    return min_max_brackets

