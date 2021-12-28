# is this a comment?????????????? cull dictionary


def cull():
	outputarray = []
	with open("dict2.txt", "r", encoding="utf8") as f:
		for line in f:
			if len(line) == 6:
				match = 0
				for chari in line:
					for charj in line:
						if chari[i] == charj[j] and i != j:
							match = + 1
				if match == 0:
					outputarray.append(line)
	with open("dict.txt", "w", encoding="utf8") as output:
		output.write("".join(outputarray))


if __name__ == "__main__":
	cull()
