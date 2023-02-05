def dictionary_selector(dictionary: dict, error_message: str = "\n\nTry again"):

    def check_length(index: int, length: int = len(dictionary)):
        return index < length

    dictionary_string = [
            f"[{i}] {key}"
            for i, key in
            enumerate(dictionary.keys())
        ]
    i = 'g'
    while type(i) != int or not check_length(i):
        print(*dictionary_string, sep="\n")

        i = input("Pick: ")

        try:
            i = int(i)
            if not check_length(i): print('\n\nTry again')
        except ValueError: print('\n\nTry again')

    return i
