def convert(number):
    """Expresses a number with Chinese numerals.

    Returns:
        A string of the Chinese characters that represent this number.
    """

    digits = [int(x) for x in str(number)]
    numbers = "零一二三四五六七八九十"

    if number <= 10:
        return numbers[number]
    elif number < 20:
        return "十" + convert(number - 10)
    elif number < 100:
        tens_place = digits[0]
        ones_place = digits[1]

        content = ""

        if ones_place > 0:
            content = convert(ones_place)

        return convert(tens_place) + "十" + content
    elif number < 1000:
        hundreds_place = digits[0]
        tens_place = digits[1]
        ones_place = digits[2]

        content = ""

        if tens_place == 0 and ones_place == 0:
            pass
        elif tens_place <= 1:
            content = convert(tens_place) + convert(tens_place * 10 + ones_place)
        else:
            content = convert(tens_place * 10 + ones_place)

        return convert(hundreds_place) + "百" + content
    elif number < 10000:
        thousands_place = digits[0]
        hundreds_place = digits[1]
        tens_place = digits[2]
        ones_place = digits[3]

        content = ""

        if hundreds_place == 0:
            if tens_place == 0:
                if ones_place > 0:
                    content = "零" + convert(ones_place)
                else:
                    pass
            elif tens_place == 1:
                content = "零一" + convert(tens_place * 10 + ones_place)
            else:
                content = "零" + convert(tens_place * 10 + ones_place)
        else:
            content = convert(hundreds_place * 100 + tens_place * 10 + ones_place)

        return convert(thousands_place) + "千" + content
