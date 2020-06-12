'''
-------------------------------------------
Python Music Player
Sammy Potter – July 2019
Python 3.6.5
-------------------------------------------
Python Music Player plays .mp3 audio files
from the music folder using vlc, tkinter,
cv2, and PIL. It is designed to play
downloaded youtube mixes (~40 min each),
containing many different songs.
-------------------------------------------
Folder tree (required)
music ->	.mp3 files
		python_music_player.py
		Python Music Player.command
		player ->	gui
					thumbnails
					timestamps
-------------------------------------------						
'''

#libraries
import time, datetime
import csv
import cv2
import os
import vlc
from tkinter import *
import tkinter.ttk
from tkinter.ttk import *
from PIL import Image
from PIL import ImageTk

'''
VLC PLAYER STATES
	1: 'Opening',
	2: 'Buffering',
	3: 'Playing',
	4: 'Paused',
	5: 'Stopped',
	6: 'Ended',
	7: 'Error'
'''

#keeps track of the passage of time (while the player is not paused)
seconds = 0
def count_second():
	global seconds
	try:
		if player.get_state() == 3:
			seconds += 1
			root.after(1000, count_second)
		else:
			root.after(1, count_second)
	except NameError:
		root.after(1, count_second)

#keeps track of the playhead and skips song when previous one is done, and adjusts volume (from slider input)
currentSong = 0
def song_handler():
	global currentSong, timestamps_seconds, seconds, song_titles, player, songProgress
	try:
		try:
			if seconds == (timestamps_seconds[currentSong + 1]):
				currentSong += 1
		except IndexError:
			pass
		player.audio_set_volume(volume_fromslider) #nice
	except NameError:
		pass
	root.update_idletasks()
	root.after(100, song_handler)

#is called at the end of load_info(), uses data from load_info to start playing
def start_mix(name_noextension):
	global player, currentSong, mix_end_seconds, songProgress, seconds, isPaused
	vlc_instance = vlc.Instance("--quiet")
	player = vlc_instance.media_player_new()
	#for VSCODE run:	media = vlc_instance.media_new("./" + name_noextension + ".mp4")
	media = vlc_instance.media_new(music_folder_path + '/' + name_noextension + ".mp3")
	currentSong = 0
	seconds = 0
	player.set_media(media)
	player.play()
	root.update_idletasks()
	time.sleep(0.05)
	mix_end_seconds = round((player.get_length() / 1000), 0)
	timestamps_seconds.append(mix_end_seconds)
	playButton.config(image=iconPAUSE, text="PAUSE")
	isPaused = False

#loads mix info, configures buttons, and reads mix/track data into the script
def load_info(mode, mix_title):
	global mixName, player, music_folder_noextensions, textFileItems_cleannames, timestamps_seconds, song_titles, artists, thumbnail_box, iconTHUMBNAIL, mixGenre, allGenres, availible_genres
	#mode 0 runs in order to display items in the menu
	if mode == 0:
		availible_genres = []
		temp_availible_genres = []
		textFileItems_cleannames = []
		textFileItems_rawnames = sorted(os.listdir(timestamps_path))
		allGenres = []
		for k in textFileItems_rawnames:
			if not k.endswith('.txt'):
				textFileItems_rawnames.remove(k)
		for item in textFileItems_rawnames:
			filePath_init = open(timestamps_path + item)
			fileRead_init = csv.reader(filePath_init)
			fetchData_init = fileRead_init
			fetchItems_init = []
			for row in fetchData_init:
				fetchItems_init.append(row)
			temp_multigenre = []
			for k in fetchItems_init[1]:
				temp_multigenre.append(str(k).strip("[],'\""))
			allGenres.append(temp_multigenre)
			for t in allGenres:
				if type(t) == list:
					for s in t:
						temp_availible_genres.append(s)
				else:
					temp_availible_genres.append(t)
			if str(fetchItems_init[1]).strip("[]'\"") == 'single':
				textFileItems_cleannames.append((str(fetchItems_init[0]).strip("[]'\""))) # + " (single)"
			elif str(fetchItems_init[1]).strip("[]'\"") != 'single':
				textFileItems_cleannames.append((str(fetchItems_init[0]).strip("[]'\""))) # + " – A " + (str(fetchItems_init[1]).strip("[]'\"")) + " Mix"
		availible_genres.append(temp_availible_genres)
		availible_genres = list(dict.fromkeys(temp_availible_genres))
		availible_genres.insert(0, 'All')

	#mode 1 reads timestamp file data, loads track image, and configures labels
	elif mode == 1:
		filePath = open(timestamps_path + mix_title + ".txt")
		fileRead = csv.reader(filePath)
		fetchData = fileRead
		fetchItems = []
		for row in fetchData:
			fetchItems.append(row)
		mixName = str(fetchItems[0]).strip("[]'\"")
		mixName = mixName.replace('\u3000', '')
		mixGenre = []
		for o in fetchItems[1]:
			mixGenre.append(o.strip("[]'").replace('\u3000', ''))
		for i in range(0, 2):
			fetchItems.remove(fetchItems[0])
		timestamps_fancy = []
		artists = []
		song_titles = []
		for item in fetchItems:
			song = item
			timestamps_fancy.append(str(song[0]).strip("[]'"))
			artists.append(str(song[1]).strip("[]'"))
			song_titles.append(str(song[2]).strip("[]'"))
		timestamps_seconds = []
		for item in timestamps_fancy:
			converted_time = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(item.split(":"))))
			timestamps_seconds.append(converted_time)
		try:
			iconTHUMBNAIL = PhotoImage(file=thumbnail_path + mix_title + ".png")
		except:
			iconTHUMBNAIL = PhotoImage(file=thumbnail_path + "no_image.png")
			print('no image found')
		thumbnail_box.config(image=iconTHUMBNAIL)
		songProgress.config(value=0)
		root.update_idletasks()

#called when a mix is selected from the menu, closes the menu and starts the mix
menu_isopen = False
def close_menu():
	global menu_window, menu_isopen
	menu_window.destroy()
	menu_isopen = False

#handles a selection from the mix menu
def menu_button_handler(event):
	try:
		player.stop()
	except NameError:
		pass
	for i in range(0, len(textFileItems_cleannames)):
		if event == textFileItems_cleannames[i]:
			foundIndex = i
	load_info(1, music_folder_noextensions[foundIndex])
	start_mix(music_folder_noextensions[foundIndex])
	close_menu()

def genre_button_handler(event):
	global availible_genres, selected_genre
	close_menu()
	selected_genre = event
	create_menu_window()

#open the menu window and display all the availible mixes
def create_menu_window():
	global menu_window, music_folder_noextensions, menu_isopen, mixName, player, availible_genres, selected_genre, allGenres, textFileItems_cleannames
	if not menu_isopen:
		music_folder_with_extensions = sorted(os.listdir(music_folder_path))
		files_to_delete = []
		for k in music_folder_with_extensions:
			if (k.startswith('.')) or (not k.endswith('.mp3')):
				files_to_delete.append(k)
		for j in files_to_delete:
			music_folder_with_extensions.remove(j)
		music_folder_noextensions = []
		for item in music_folder_with_extensions:
			music_folder_noextensions.append(item[:-4])
		menu_window = Toplevel()
		menu_window.configure(background='#d9d9d9')
		menu_window.title('MENU')
		load_info(0, '')
		filtered_mix_names = []
		for j in range(0, len(textFileItems_cleannames)):
			for d in allGenres[j]:
				if (d == selected_genre) or (selected_genre == 'All'):
					filtered_mix_names.append(textFileItems_cleannames[j])
					break
		totalItems = int(len(filtered_mix_names)) + int(len(availible_genres))
		buttonsPacked = 0
		buttonsPacked_inOneColumn = 0
		row = 0
		col = 0
		items_perColumn = 15
		menu_items_style = Style()
		menu_items_style.configure('my.TButton', font=(global_font, global_font_size))
		while buttonsPacked != totalItems:
			for genre in availible_genres:
				Button(menu_window, style='my.TButton', text=genre, command=lambda genre=genre: genre_button_handler(genre)).grid(row=row, column=col)
				if buttonsPacked_inOneColumn != items_perColumn - 1:
					row += 1
					buttonsPacked_inOneColumn += 1
				elif buttonsPacked_inOneColumn == items_perColumn - 1:
					row = 0
					col += 1
					buttonsPacked_inOneColumn = 0
				buttonsPacked += 1
			row = 0
			col += 1
			buttonsPacked_inOneColumn = 0
			for item in filtered_mix_names:
				Button(menu_window, style='my.TButton', text=item, command=lambda item=item: menu_button_handler(item)).grid(row=row, column=col)
				if buttonsPacked_inOneColumn != items_perColumn - 1:
					row += 1
					buttonsPacked_inOneColumn += 1
				elif buttonsPacked_inOneColumn == items_perColumn - 1:
					row = 0
					col += 1
					buttonsPacked_inOneColumn = 0
				buttonsPacked += 1

		windowWidth = menu_window.winfo_reqwidth()
		windowHeight = menu_window.winfo_reqheight()
		positionRight = int(menu_window.winfo_screenwidth()/5 - windowWidth/5)
		positionDown = int(menu_window.winfo_screenheight()/5 - windowHeight/5)
		menu_window.geometry("+{}+{}".format(positionRight, positionDown))

		menu_window.protocol("WM_DELETE_WINDOW", close_menu) #THIS WORKS
		menu_isopen = True

#start or stop the player
isPaused = False
def play_pause():
	global isPaused, iconPAUSE, iconPLAY
	if isPaused:
		try:
			print('playing')
			playButton.config(image=iconPAUSE, text="PAUSE")
			player.play()
			isPaused = False
		except NameError:
			isPaused = False
	else:
		try:
			print('paused')
			playButton.config(image=iconPLAY, text="PLAY")
			player.pause()
			isPaused = True
		except NameError:
			isPaused = True

#quit the app (called when system window close button (small red circle in top left) is clicked)
def quit_app():
	print('quitting')
	exit()

#skip forward one song
def skip():
	global currentSong, timestamps_seconds, seconds, songProgress
	if song_titles[currentSong] != song_titles[len(song_titles) - 1]:
		print('skipping')
		currentSong += 1
		seconds = timestamps_seconds[currentSong]
		player.set_time(seconds * 1000)
		root.update_idletasks()
	else:
		print('cant skip (last song in mix)')
	
#skip backward one song
def back():
	global currentSong, timestamps_seconds, seconds
	if currentSong != 0:
		print("going back")
		currentSong -= 1
		seconds = timestamps_seconds[currentSong]
		player.set_time(seconds * 1000)
	else:
		print("cant go back (first song in mix)")

#opens the menu (called by the menu button)
def open_menu():
	print('opening menu')
	create_menu_window()

#track the status of the vlc media player and make changes to the GUI
def trackStatus():
	global player, mixName, mixGenre, iconTHUMBNAIL, seconds
	try:
		if player.get_state() == 6:
			root.title('No mix selected')
			songLabel.config(text='– Click MENU to choose a mix –')
			iconTHUMBNAIL = PhotoImage(file=thumbnail_path + "no_image.png")
			thumbnail_box.config(image='')
		else:
			try:
				mixGenre.sort(key=str.lower)
				mixGenreString = '/'.join(mixGenre)
				if 'single' in mixGenre:
					root.title(mixName + " (single)")
				else:
					root.title(mixName + " – A " + mixGenreString + " Mix")
				songLabel.config(text='Now playing: ' + song_titles[currentSong] + ' by ' + artists[currentSong] + '\n' + (str(datetime.timedelta(seconds=(seconds - timestamps_seconds[currentSong])))[2:]) + '                                                                                   ' + (str(datetime.timedelta(seconds=(timestamps_seconds[currentSong + 1] - seconds)))[2:]))
			except IndexError:
				pass
		root.update_idletasks()
	except NameError:
		pass
	root.after(1000, trackStatus)

#updates the progress bar
def pbar_update():
	global timestamps_seconds, seconds, player, songProgress
	try:
		if player.get_state() != 6:
			try:
				songProgress['value'] = (((seconds - timestamps_seconds[currentSong]) / (timestamps_seconds[currentSong + 1] - timestamps_seconds[currentSong])) * 100)
				root.update_idletasks()
			except (NameError, IndexError):
				pass
		else:
			songProgress['value'] = 0
	except NameError:
		pass
	root.after(1000, pbar_update)

#pass information from the volume slider
def adjust_volume(self):
	global volume_fromslider
	volume_fromslider = int(volume_slider.get())

#tkinter window initial declaration and config  
class Player_window(Frame):
	def __init__(self, master=None):
		global iconSTOP, iconPAUSE, iconPLAY, playButton, songLabel, songProgress, volume_slider, thumbnail_box, iconTHUMBNAIL
		Frame.__init__(self, master, height=50, width=100)
		#styling
		root.style = tkinter.ttk.Style()
		root.style.theme_use("classic") #styles: clam, alt, default, classic
		label_style = Style()
		label_style.configure('my.TLabel', font=(global_font, global_font_size))

		#slider
		volume_slider = Scale(master, from_=0, to=100, len=110, orient=HORIZONTAL, command=adjust_volume)
		volume_slider.set(75)

		#buttons
		skipBackwardButton = Button(master, image=iconBACK, command=back)
		playButton = Button(master, image=iconPAUSE, command=play_pause)
		skipForwardButton = Button(master, image=iconSKIP, command=skip)
		menuButton = Button(master, image=iconMENU, command=open_menu)

		#labels
		songLabel = Label(master, style='my.TLabel', text='– Click MENU to choose a mix –', justify=CENTER)
		songProgress = Progressbar(master, orient=HORIZONTAL, length=400, mode='determinate')
		thumbnail_box = Label(master) #image=iconTHUMBNAIL

		#packing items
		thumbnail_box.pack(side=TOP)
		songLabel.pack(side=TOP)
		songProgress.pack(side=TOP)
		skipBackwardButton.pack(side=LEFT)
		playButton.pack(side=LEFT)
		skipForwardButton.pack(side=LEFT)
		menuButton.pack(side=LEFT)
		volume_slider.pack(side=LEFT)

		#extra important stuff
		root.configure(background='#d9d9d9')
		root.title('No mix selected')
		root.protocol("WM_DELETE_WINDOW", quit_app)
		self.master = master

#turn tkinter on
root = Tk()

#important paths
full_path = str(os.path.realpath(__file__))
music_folder_path = (full_path.replace('/python_music_player.py', ''))
guipath = music_folder_path + "/player/gui/"
thumbnail_path = music_folder_path + "/player/thumbnails/"
timestamps_path = music_folder_path + "/player/timestamps/"

#verifies the existence of necessary folders
def verify_have_folders():
	verify_checks = [False, False, False, False]
	verify_player_folder = os.listdir(music_folder_path)
	for item in verify_player_folder:
		if item == 'player':
			verify_checks[0] = True

	if verify_checks[0] != True:
		print('Fatal error, missing \"player\" folder.')
		quit_app()

	necessary_folders = ['gui', 'thumbnails', 'timestamps']
	if verify_checks[0] == True:
		verify_player_folder_contents = os.listdir(music_folder_path + '/player')
		for w in verify_player_folder_contents:
			if w not in necessary_folders:
				verify_player_folder_contents.remove(w)
		verify_player_folder_contents.remove('.DS_Store')
		verify_player_folder_contents.sort()
		for i in range(0, len(verify_player_folder_contents)):
			if verify_player_folder_contents[i] == necessary_folders[i]:
				verify_checks[i+1] = True
			else:
				verify_checks[i+1] = False

	if verify_checks != [True, True, True, True]:
		print("Fatal error. Missing folder(s):")
		for i in range(0, len(necessary_folders)):
			if not verify_checks[i]:
				print('* ' + necessary_folders[i])
		quit_app()

verify_have_folders()

#make images
iconSTOP = PhotoImage(file=guipath + "stop.png")
iconPLAY = PhotoImage(file=guipath + "play.png")
iconPAUSE = PhotoImage(file=guipath + "pause.png")
iconSKIP = PhotoImage(file=guipath + "skip.png")
iconBACK = PhotoImage(file=guipath + "back.png")
iconMENU = PhotoImage(file=guipath + "menu.png")
iconTHUMBNAIL = PhotoImage(file=thumbnail_path + "no_image.png") #placeholder image to display when no thumbnail is found

#global text styling
global_font = 'DIN Alternate' #default system font is cool too
global_font_size = 15

#more init
selected_genre = 'All'
app = Player_window(root)
root.after(0, trackStatus)
root.after(0, pbar_update)
root.after(0, count_second)
root.after(0, song_handler)
root.mainloop()
