
# comic_viewer

Comic Viewer is a local comic image viewer that allows you to browse through your favorite comics stored on your computer. It supports selecting comics by date and comic shortcodes for easy organization and access.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [WebUI Usage](#webui-usage)
- [Adding and Editing Comics](#adding-and-editing-comics)
- [File Naming Convention](#file-naming-convention)
- [Known Issues](#known-issues)

## Features

- Simple and intuitive GUI for managing your comic collection.
- View locally stored comic images by selecting the date.
- Supports multiple comics with unique shortcodes.
- Add and edit comic details such as name, URL and shortcode.
- WebUI for accessing comics from your browser.

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

## WebUI Usage

1. **Run the web application**

     ```bash
     python comic_web.py
     ```

   - Open your web browser and navigate to `http://127.0.0.1:5000`.
   - Log in using the admin credentials displayed in the command line.

2. **Passwords:**

   - On the first run, an admin user will be created with a randomly generated password. The username and password will be displayed in the command line. Make sure to save this password for future logins.

     Example output:
     ```
     Username: admin, Password: generated_password
     ```

   - Click on "Change Password" at the bottom of the left panel to change the admin password.

## Known Issues

- None
