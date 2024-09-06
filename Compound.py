# Moksh
# -*- coding: utf-8 -*-

import os
import sys
from datetime import date

def GetResolve():
    try:
    # The PYTHONPATH needs to be set correctly for this import statement to work.
    # An alternative is to import the DaVinciResolveScript by specifying absolute path (see ExceptionHandler logic)
        import DaVinciResolveScript as bmd
    except ImportError:
        if sys.platform.startswith("darwin"):
            expectedPath="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
        elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
            import os
            expectedPath=os.getenv('PROGRAMDATA') + "\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules\\"
        elif sys.platform.startswith("linux"):
            expectedPath="/opt/resolve/Developer/Scripting/Modules/"

        # check if the default path has it...
        print("Unable to find module DaVinciResolveScript from $PYTHONPATH - trying default locations")
        try:
            import imp
            bmd = imp.load_source('DaVinciResolveScript', expectedPath+"DaVinciResolveScript.py")
        except ImportError:
            # No fallbacks ... report error:
            print("Unable to find module DaVinciResolveScript - please ensure that the module DaVinciResolveScript is discoverable by python")
            print("For a default DaVinci Resolve installation, the module is expected to be located in: "+expectedPath)
            sys.exit()

    return bmd.scriptapp("Resolve")
	
# Global Variables
resolve = GetResolve()
projectManager = resolve.GetProjectManager() # get manager
proj = projectManager.GetCurrentProject() # get project
mediaPool = proj.GetMediaPool()
tl = project.GetCurrentTimeline() # get tl
################################################################################################
# Functions #
#############

class Clip:

	# all this class needs is a timeline item
	def __init__(self, tl_item):
		self.item = tl_item

	# confirms self is in the mediapool and not a redx or 2pop
	# input: none
	# output: Bool
	def isMedia(self):
		media = self.item.GetMediaPoolItem()
		if media == None:
			return False
		else:
			return True
			
	def getMedia(self):
		return self.item.GetMediaPoolItem()

	def get_name(self):
		return self.item.GetName()

	# returns fps of self
	# input: none
	# output: float
	def fps(self):
		if self.isMedia():
			media = self.item.GetMediaPoolItem()
			numb = float(media.GetClipProperty('FPS'))
		else:
			numb = float(23.976)
		return numb
	
	# determines if media has df
	# input: none
	# output: Bool
	def dropframe(self):
		media = self.item.GetMediaPoolItem()
		drop = media.GetClipProperty('Drop frame')
		if drop == "0":
			return False
		else:
			return True
		
	# gets start frame of media in mediapool
	# input: none
	# output: int
	def mediaStartFrame(self):
	
		media = self.item.GetMediaPoolItem()
		tc = media.GetClipProperty('Start TC')	# this is in ##:##:##:## format
		
		# check to see if framerate is matching
		if int(tc[9:]) > self.fps():
			raise ValueError ('Timecode to frame rate mismatch.', tc, self.fps)
			
		# convert all strings to ints
		hours = int(tc[:2])
		minutes = int(tc[3:5])
		seconds = int(tc[6:8])
		frames = int(tc[9:])
		
		totalMinutes = int(60 * hours + minutes)	# convert hours to mins and sum
		
		# Drop Frame Calc
		if self.dropframe():
			
			dropFrames = int(round(self.fps() * 0.066666))
			timeBase = int(round(self.fps()))
			
			hourFrames = int(timeBase * 60 * 60)
			minuteFrames = int(timeBase * 60)
			
			frm = int(((hourFrames * hours) + (minuteFrames * minutes) + (timeBase * seconds) + frames) - (dropFrames * (totalMinutes - (totalMinutes // 10))))
		
		# non df calc
		else:
			frameBase = int(round(self.fps()))
			frm = int((totalMinutes * 60 + seconds) * frameBase + frames)
			
		return frm
		
	# Shortcuts to get mediapool endframe, effective startframe, and effective endframe
	# where an effective endframe is the in-out points of media on timeline but as source frame numbers
	# input: none
	# output: int
	def startFrame(self):
		return self.mediaStartFrame() + int(self.item.GetLeftOffset())
	
	
	def start_tc(self):
		frame = self.startFrame()
		
		fps = int(round(float(tl.GetSetting('timelineFrameRate'))))
		timecode = []	

		timecode.append(str(frame // (3600 * fps)).rjust(2, '0')) # hours 
		frame = frame % (3600 * fps) # remove the hours from frame
		timecode.append(str(frame // (60 * fps)).rjust(2, '0')) # mins
		frame = frame % (60 * fps) # remove the mins from frame
		timecode.append(str(frame // fps).rjust(2, '0')) # secs
		frame = frame % fps
		timecode.append(str(frame).rjust(2, '0')) #frames	

		tc_str = ':'.join(timecode)

		return tc_str
			
	# shortcut to get filename of self
	# input: none
	# output: str or None
	def filename(self):
		if self.isMedia():
			media = self.item.GetMediaPoolItem()
			return media.GetClipProperty('File Name')
		else:
			return None
		
	def __str__(self):
		return "Clip Item [" + str(self.filename()) + "]"


# Creates compound clip from currently selected
def main():

	tlItem = timeline.GetCurrentVideoItem() # get clip
	clip = Clip(tlItem)
	start = clip.start_tc()
	name = clip.get_name()
	
	if clip.isMedia():
		start = clip.start_tc()
		tl.CreateCompoundClip([tlItem], {"startTimecode" : start, "name" : "_" + name})
	else:
		tl.CreateCompoundClip([tlItem], {"startTimecode" : "00:00:00:00", "name" : name})

main()
