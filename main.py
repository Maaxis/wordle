import random
import clipboard
from rich import print
from cryptography.fernet import Fernet
import cryptography
from time import sleep

key = b'QKeYs7FIni2fKtpui16fCMxAWCy6SRvtuh5mFdGnrms='
fernet = Fernet(key)
wordDict = "dict.txt"
answerDict = "dict.txt"


def checkFiles(file):
	try:
		f = open(file, "r", encoding="utf8")
		f.close()
	except FileNotFoundError:
		print("Error: {} is missing. Ensure it is in the same folder as wordle.exe, then restart".format(answerDict))
		sleep(10)
		exit()


# generate a new word by reading the dictionary of eligible words
def randomWord():
	wordlist = []
	with open(answerDict, "r", encoding="utf8") as f:
		for line in f:
			wordlist.append(line)
	if len(wordlist) < 11:
		print("Error: Found less than 10 words in {}. Ensure the file is not empty, then restart".format(answerDict))
		sleep(10)
		exit()
	word = random.choice(wordlist).strip()
	return word


def checkAndColor(guess, correct, keyboard):
	color_word = []
	for i in range(0, len(guess)):
		char = guess[i]
		greenw = "[green]{}[/]".format(char.upper())
		yelloww = "[yellow]{}[/]".format(char.upper())
		redw = "[red]{}[/]".format(char.upper())
		if char in correct:
			if guess[i] == correct[i]:  # if letter exists at this place, make text green
				if yelloww in keyboard:
					keyboard.remove(yelloww)
				elif greenw in keyboard:
					keyboard.remove(greenw)
				elif redw in keyboard:
					keyboard.remove(redw)
				color_word.append(greenw)
				keyboard.append(greenw)
			else:  # if letter exists but in wrong place, make text yellow
				color_word.append(yelloww)
				if yelloww in keyboard:
					keyboard.remove(yelloww)
					keyboard.append(yelloww)
				elif greenw not in keyboard:
					keyboard.append(yelloww)
		else:  # else make text red
			if yelloww in keyboard:
				keyboard.remove(yelloww)
			elif greenw in keyboard:
				keyboard.remove(greenw)
			elif redw in keyboard:
				keyboard.remove(redw)
			color_word.append(redw)
			keyboard.append(redw)
	word_s = ''.join(color_word)
	keys = ''.join(reformat(keyboard))
	result = [word_s, keys]
	return result


# for printing the keyboard
def reformat(dictionary):
	qwerty = ["\t", 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', "\n\t", 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K',
	          'L', "\n\t", 'Z', 'X', 'C', 'V', 'B', 'N', 'M']
	greens = []
	yellows = []
	reds = []
	keyboard = []
	for i in range(0, len(qwerty)):
		greens.append("[green]{}[/]".format(qwerty[i]))
		yellows.append("[yellow]{}[/]".format(qwerty[i]))
		reds.append("[red]{}[/]".format(qwerty[i]))
	for j in range(0, len(qwerty)):
		if greens[j] in dictionary:
			keyboard.append(greens[j])
		elif yellows[j] in dictionary:
			keyboard.append(yellows[j])
		elif reds[j] in dictionary:
			keyboard.append(reds[j])
		else:
			keyboard.append(qwerty[j])
	return keyboard


# print everything formatted nicely
def printCheck(word, keyboard, guesses, guess):
	check = checkAndColor(guess, word, keyboard)
	print("\n" + check[1])
	print("\t__________")
	guesses.append('\t' + check[0])
	print('\n'.join(guesses))


# check that entered guess is valid
def validate(guess):
	if len(guess) != 5:  # word must be 5 letters
		return 2
	else:  # word must exist in full dictionary
		diction = []
		with open(wordDict, "r", encoding="utf8") as f:
			for line in f:
				diction.append(line.strip())
			if guess in diction:
				return 0
			else:
				return 1


# input guess
def game(word, keyboard, turn, guesses):
	guess = input("\nTurn {}: ".format(str(turn))).lower()
	if guess.lower() == "menu":
		main()
	else:
		if guess == word:
			printCheck(word, keyboard, guesses, guess)
			print("You did it! Turns: {}".format(str(turn)))
			again = input("Hit ENTER to play again (or type \"MENU\").\n")
			if again.lower() == "menu":
				main()
			else:
				initialize()
		else:
			if validate(guess) == 0:
				printCheck(word, keyboard, guesses, guess)
				turn += 1
			elif validate(guess) == 1:
				print("That's not a word!")
			else:
				print("Enter a 5 letter word.")
			game(word, keyboard, turn, guesses)


# encrypt, decrypt, multiplayer, and playMulti are all for custom games
def encrypt(string):
	encrypted = fernet.encrypt(string.encode())
	encrypted_string = str(encrypted, encoding='utf-8')
	return encrypted_string


def decrypt(token):
	decrypted = fernet.decrypt(bytes(token, encoding="utf-8"))
	decode = decrypted.decode('utf-8')
	return decode


def multiMenu():
	print("\nCUSTOM GAME")
	choice = input("[1] Randomize a new game\n[2] Play a previously generated game\n[3] Back\n")
	if choice == "1":
		wordlist = []
		num = input("How many rounds?\n")
		if num.lower() == "menu":
			main()
		else:
			try:
				if int(num) > 10:
					print("The maximum number of rounds is 10.")
					multiMenu()
				else:
					for i in range(0, int(num)):
						wordlist.append(randomWord())
					words = ','.join(wordlist)
					print("New game generated! The following token has been copied to your clipboard.")
					token = (encrypt(words))
					print("[white]" + token + "[/]")
					clipboard.copy(token)
					play = input("Play now? y/n: ")
					if play.lower() == "y":
						multiPlay(words)
					else:
						main()
			except(ValueError, TypeError):
				print("Enter an integer.")
				multiMenu()
	if choice == "2":
		token = input("Enter the game token:\n")
		if token.lower() == "menu":
			main()
		else:
			try:
				words = decrypt(token)
				multiPlay(words)
			except (cryptography.fernet.InvalidToken, TypeError):
				print("Invalid token! Use a token generated from option 1 of the custom game setup.")
				multiMenu()
	else:
		main()


def multiPlay(words):
	wordlist = words.split(",")
	for i in range(0, len(wordlist)):
		print("ROUND {}/{}".format(str(i + 1), str(len(wordlist))))
		keyboard = []
		guesses = []
		game(wordlist[i], keyboard, 1, guesses)


def intro():
	print("[green]Max's Bad Wordle Clone v1.0[/]")


def printHelp():
	print(
		"\nBased on Wordle from [link=https://www.powerlanguage.co.uk/wordle/]https://www.powerlanguage.co.uk/wordle/[/link].")
	print("\n\tHOW TO PLAY")
	print("Guess the WORDLE in any number of tries.")
	print(
		"After each guess, the color of the tiles will change to show how close your guess was to the word. Example: ")
	print("[green]W[/][yellow]EA[/][green]R[/green][red]Y[/red]")
	print("The letters W and R are in the word and in the correct spots.")
	print("The letters E and A are in the word but in the wrong spots.")
	print("The letter Y is not in the word in any spot.")
	print("\n\tHOW TO USE")
	print("You can navigate this software by entering commands.")
	print("For menu options, type the number next to the option you'd like to select and press ENTER.")
	print("To make a word guess in-game, simply type in the word and press ENTER.")
	print("You can return to the main menu by typing MENU from anywhere in the program.")
	print("Report bugs or feedback to Max!")


def initialize():
	print("Type MENU at any time to return to the menu.")
	word = randomWord()
	keyboard = []
	guesses = []
	game(word, keyboard, 1, guesses)


'''
def getColor(color, cb):
	print("this isn't done yet sorry")
	main()


def options():
	print("this isn't done yet sorry")
	print("[1] Colorblind settings\n[2] Back")
	main()
'''


def main():
	checkFiles(wordDict)
	checkFiles(answerDict)
	print("\nMAIN MENU")
	menu = input("[1] Play now\n[2] Custom game setup (multiplayer)\n[3] Help\n[4] Exit\n")
	if menu == "1":
		initialize()
	elif menu == "2":
		multiMenu()
	elif menu == "3":
		printHelp()
	elif menu == "4":
		exit()
	else:
		print("\nTo select a menu option, type only the number and press ENTER.")
		main()


if __name__ == "__main__":
	intro()
	main()
