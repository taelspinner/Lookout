# Lookout
A Python script that tells you which of your images are being used in other profiles on F-List.

Just download and run lookout.py from the Command Prompt. You need Python 3.X and the requests library. You'll be asked to provide your login credentials, which are required to generate a ticket so that the script can get the list of images from your character.

The first time you run it, you'll need to download the hash DB from the server. This may take a while.

The script will only return the URLs of the images that are duplicated, not the profiles that are using them. I can't reference these images back to the profiles they belong to, but F-List staff probably can, so ask them. Bear in mind that if other people's characters are in your images, and they also use that art, it will return those images. So double check.

# Dependencies
requests
