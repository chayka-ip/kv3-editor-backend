# About

Main purpouse of the project is to simplify editing KV3 files which are used for different tasks in videogames developed by Valve (AI scripting, cutscenes, etc...).
We provide:
	- GUI to work with nested structures
	- Editing node data
	- Commenting of nodes
	- Import(export) from(to) KV3 file format 


Hosted on: L https://kv3-editor-frontend.herokuapp.com/

Sever might be sleeping, so please, wait a bit and update the page.
NB. The final visual style was supposed to be designed by a friend of mine, but he didn't do it (: 

# Usage

 - Upload valid KV3 file or create new one by adding New Node 
 - Nodes must be connected. Use mouse dragging between blue and cyan pins
 - Edit data in the left window ("name" field must be filled)
 - Use Arrange button to marshall all nodes by hierarchy
 - Download the result
 

# KV3 File Format

Valve gives a brief knowledge about the format, but many important nuances aren't mention. 

https://developer.valvesoftware.com/wiki/Dota_2_Workshop_Tools/KeyValues3

KeyValues3 is a Valve developed data format. It is similar in structure to JSON, but supports binary encodings,
versioning, and data annotations. The text syntax also has some minor ergonomic improvements 
(support for single- and multi-line comments, trailing commas, and multi-line strings.)

The header of a text KV3 file specifies the encoding and format of the file. 
These are specified as GUIDs rather than integers to prevent unintentional collision if two people 
change format or encoding simultaneously in separate projects.

For the average user, GUIDs at the top of a KV3 file should always be the same.

Multiline String Literals

Multiline string format is:

Begin string with three unescaped quotes followed by an immediate newline (eg. the buffer looks like "\"\"\"\n")
End string with a newline followed by three unescaped quotes (eg. the buffer looks like "\n\"\"\"")
All characters between the two newlines (non-inclusive) are taken literally, with no normal escape characters.

Flags

KV3 keys can have flags to annotate their value as having special importance to some system. 
Currently the only flags are "resource" and "deferred_resource" to indicate that the flagged 
string is a resource reference. (ie. used for models and textures referenced by a particle system.)


Property are declared one per line. If property's value is object or array then 
assignment after '=' might be moved to next lines

# Implementation

Inline/multiline comments are supported. You can comment above the property or object/array.

Inline declaration of arrays/objects is not supported.

Raw file can be converted to json in expecting way, but with several details.

All values are converted into corresponding type which is supported in json.

All string types are converted into single line string, but inner '\n' are preserved.

All comments are converted into multiline comment ('/*', '*/' are not included).
If item doesn't have any comment - this field is ignored.

Complex structures (arrays and objects) have corresponding 'data_type' property for easier indication.

Array items doesn't have 'name' property.