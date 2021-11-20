# Landsat Pine Glacier Visualization
A visualization of the Antarctic Pine Island Glacier from 2013 to 2021. Data retrieved using M2M api and Landsat 8 imagery.

## Filenames
- pineGlacier.mp4: Final visualization.
- ImportData.py: Modified from USGS M2M API examples. Downloads scenes from specific dataset using metadata filters. Configured to only download images of Pine Island Glacier. Note: Under existing filter configuration total download size is ~50 gb.
- processData.py: Processes download scenes to create a combined RGB image outputed to a png file through matplotlib. Created files are named by imagery date.
- movieAssembler.py: Collectes images from processData.py and creates a .avi video file, sorted by date.
