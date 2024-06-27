def romeal_to_number(romeal):
    romeal_map = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

    number = 0
    romeal = romeal.upper()

    letter_index = 0
    while letter_index < len(romeal):
        letter = romeal[letter_index]
        next_letter = (
            romeal[letter_index + 1] if letter_index + 1 < len(romeal) else None
        )
        next_next_letter = (
            romeal[letter_index + 2] if letter_index + 2 < len(romeal) else None
        )
        next_next_next_letter = (
            romeal[letter_index + 3] if letter_index + 3 < len(romeal) else None
        )

        letter_value = romeal_map.get(letter, 0)
        next_letter_value = romeal_map.get(next_letter, 0) if next_letter else 0

        if (
            (letter == next_letter)
            and (next_letter == next_next_letter)
            and (next_next_letter == next_next_next_letter)
            and next_next_next_letter
        ):
            return float("nan")  # Invalid romeal number

        if letter_value < next_letter_value:
            number -= letter_value
        else:
            number += letter_value

        letter_index += 1

    return number

print(romeal_to_number("XXIII"))