
def super_splitter(text, not_alphabet, max_len=0):
    alphabet = "abcdefghijklmnopqrstuvwxyz_"
    split_list = []
    prev_split = -1
    for i, char in enumerate(text):
        if not_alphabet:
            if char not in alphabet:
                print(prev_split, i)
                split_list += [text[prev_split+1:i]]
                prev_split = i
            elif i == len(text)-1:
                split_list += [text[prev_split+1:i + 1]]

    split_list = [a for a in split_list if len(a) >= max_len]

    return split_list


def main():
    text = input("Paste text here: \n").lower()
    split_list = super_splitter(text, True, 5)
    print(split_list)

if __name__ == "__main__":
    main()
