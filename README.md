
Audio samples of resulting melodies available on SoundCloud: 
[Robot Music](https://soundcloud.com/aprilmayplay/sets/computer-generated)



Disclaimer: I wrote this a million years ago (i.e. in college when first learning Python). I have not revisited since so I refuse to endure any shaming about it. :)

This code implements a genetic algorithm that generates
4-bar melodies.  Individuals are stored as lists of 64 tuples.  The
first element of each tuple is a pitch value, and the second is a
style value.  The style value determines whether the note is a
rest, the end of a note, or included in a link to the next note.  The
fittest set of 64 tuples chosen are sent to output.

The driver function to be called is genetic_algorithm().

Features used for fitness were inspired by both
Towsey 2001 and Milkie and Chestnutt 2001.
