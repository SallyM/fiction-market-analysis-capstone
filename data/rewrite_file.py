with open('data/small.json', 'r') as f:
    with open('data/small_formatted.json', 'a') as output_file:
        for line in f:
            if '}{' in line:
                line1, line2 = line.split('}{')
                output_file.write(line1 + "}," + "\n")
                output_file.write("{" + line2)
            else:
                output_file.write(line)
