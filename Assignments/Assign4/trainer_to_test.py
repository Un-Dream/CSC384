with open("training2.txt", "r") as f:
    lines = f.readlines()

with open("test2.txt", "w") as f:
    for line in lines:
        fields = line.split(" : ")
        stripped_fields = [field.strip() for field in fields]
        new_line = stripped_fields[0] + "\n"
        f.write(new_line)