# comic_viewer

Comic Viewer is a local comic image viewer that allows you to browse through your favorite comics stored on your computer. It supports selecting comics by date and comic shortcodes for easy organization and access.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Adding and Editing Comics](#adding-and-editing-comics)
- [File Naming Convention](#file-naming-convention)
- [Known Issues](#known-issues)

## Features

- Simple and intuitive interface for managing your comic collection.
- View locally stored comic images by selecting the date.
- Supports multiple comics with unique shortcodes.
- Add and edit comic details such as name, URL and shortcode.

## Installation

1. Install the required dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

2. Run the application:

   ```bash
   python comic_viewer.py
   ```

## Usage

1. **Viewing Comics:**

   - Launch the application.
   - Use the date selector to choose the date of the comic you want to view.
   - The comic image will be displayed if it exists in the specified folder.

2. **Navigation:**

   - Use the arrow keys to navigate between dates:
     - Right Arrow: Next Day
     - Left Arrow: Previous Day
     - Up Arrow: Previous Week
     - Down Arrow: Next Week

## Adding and Editing Comics

1. **Adding a Comic:**

   - Click on the "Add Comic" button.
   - Fill in the details:
     - Comic Name: The display name of the comic.
     - Image Short Code: A unique short code for the file names.
   - Click "OK" to save the new comic.

## File Naming Convention

Comic Viewer expects the comic images to be named using a specific convention based on the comic's shortcode and the date.

- **Format:** `<short_code><date>.jpg` or `<short_code><date>.bmp`
- **Example:**
  - For the comic with the short code `ft` on June 25, 2024:
    - `ft240625.jpg`
    - `ft240625.bmp`

Store these images in the folder specified in the application settings or the default folder (`~/comics` or `~/Pictures/comics` on Windows).

## Known Issues

- After selecting a day or comic that fails to load, moving the window will cause the previous good comic to be displayed.
