=== UltiMaze Pro [BETA] ===

Note: Click "Workflows Diagram" in the "Info" tab to help you visualize this imformation.


--- (User Preferences > Addons > 3D Maze Generator) ---


1. Preferences
    - Save .blend File - Save .blend automatically before starting long operations
    - Save Images - Save images automatically before starting long operations
    - Save Texts - Save texts automatically before starting long operations

Depending on the size and detail of your maze it may take some time to generate. When you start a potentially time-consuming task, Maze Gen will save all enabled data types. This will allow you to force your Blender window to close without losing your work. The only time these should not be enabled is if you have a blank .blend that you are testing a maze setup in.


--- (3D View > Tools > Maze Gen) ---


2. Maze Generator
    - Generate Maze - Generate maze with current settings

    - Width - Width of the maze
    - Height - Height of the maze
    - Generate 3D Maze - When generating maze, make 3D maze
    - Allow Loops - Allow maze walking path to loop
    - Chance - 1/x chance that walking path will loop
    - Allow 'Islands' - Allow pieces connected only by a corner
    - Generate Maze From List - Generate maze from specified text block
    - List Maze - Text block to generate maze from when using 'Generate Maze From List'

    - Write Maze List - Store generated maze as a text block

These are the main maze layout settings. To create simple mazes this is the only necessary tab to use.

3. Image Converter
    - Image to Text - Convert specified image maze to text maze
    - Image Maze - Image maze to use when converting "Image to Text"
    - Text to Image - Convert specified text maze to image maze
    - List Maze - Text maze to use when converting "Text to Image"

This tab allows the creation and use of image mazes. While Maze Gen must use text mazes, and can only output text and 3D mazes, you can work with images by using this simple converter.

4. Maze Tiles [Pro]
    - Use Modeled Tiles - Use tile set when generating maze
    - Generate Tiles - Generate specified tile set
    - Tile Set - Tile set to import when generating tiles
    - Import Material - Import default material when generating tiles
    - Merge Objects - Merge duplicated tiles into one maze object when finished
    - Apply Modifiers - Apply modifiers on tile objects before merging
    - Remove Doubles - Remove double vertices after merging

    - 4 Sided Wall - Piece from tile set with 4 walls
    - 3 Sided Wall - Piece from tile set with 3 walls
    - 2 Sided Wall - Piece from tile set with 2 opposite walls
    - 1 Sided Wall - Piece from tile set with 1 wall
    - 0 Sided Wall - Piece from tile set with 0 walls
    - Wall Corner - Piece from tile set with 2 adjacent walls
    - 4 Sided Floor - 4-way intersection; used when bordered by 0 walls
    - 3 Sided Floor - 3-way intersection; used when bordered by 1 wall
    - 2 Sided Floor - 2-way straight walkway; used when bordered by 2 walls
    - 1 Sided Floor - 1-way dead-end; used when surrounded by 3 walls
    - 0 Sided Floor - Island floor; used when surrounded by 4 walls
    - Floor Corner - Turning walkway; used when bordered by 2 adjacent walls

All tile pieces will be supplied if you click generate tiles. To custom edit tiles, click generate tiles with the "Blank" tile set, then edit the imported tiles. This will ensure all rotations and scales will be accurate to correctly allow Maze Gen to put them together. "Merge Objects" should almost always be enabled: if it is not you can get a messy .blend file with hundreds or thousands of objects (depending on the size of the maze). Parenting of tile parts is supported, generate the "Piping" tile set to see a demo of how it works.

5. Batch Gen [Pro]
    - Batch Generate - Generate all stored mazes
    - Store Settings - Store current maze settings (only saves settings from "Maze Generator" tab)
    - Refresh - Refresh the batches to see how many mazes are stored
    - Batches - Number of mazes that are stored
    - Clear Mazes - Remove all stored mazes

    - Batch Index - Selected stored maze
    - Load Settings - Load settings of selected stored maze
    - Delete Setting - Delete selected stored maze

The batch generator is designed to allow you to store many mazes to generate overnight or while you are on vacation. The stored maze settings have no relationship to a particular .blend file: you can store settings from one .blend, then open another to generate the mazes.


--- (Text Editor > Tools) ---


6. Maze Generator Tools
    - List Maze

    - Invert Maze - Replace all instances 0 with 1 and vice versa in specified text block (not active text block)

    - Replace Text - Replace all instances of found string in specified text block (not active text block)
    - Find - String (text) to find
    - Replace - String (text) to replace with

These are for advanced editing of maze text files. These tools are not required for general use except for if you would like to invert walls and walkways. With generate maze from list enabled and a list maze selected, the same list maze will be automatically selected in the text editor. Hit invert maze in the text editor, then generate the inverted maze. This technique can be used to create a moat and bridge system where the walkable area is on the walls and the floor is water.