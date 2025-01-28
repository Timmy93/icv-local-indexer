-- Create the Board table
CREATE TABLE board (
  id INT AUTO_INCREMENT PRIMARY KEY,
  section_name VARCHAR(255) NOT NULL,
  board_name VARCHAR(255) NOT NULL,
  last_check DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create the TitleList table
CREATE TABLE title_list (
  id INT AUTO_INCREMENT PRIMARY KEY,
  board_id INT NOT NULL,
  FOREIGN KEY (board_id) REFERENCES board(id),
  name VARCHAR(255) NOT NULL,
  last_refresh DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create the Title table
CREATE TABLE title (
  id INT AUTO_INCREMENT PRIMARY KEY,
  board_id INT NOT NULL,
  name VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  author_id INT NOT NULL,
  date DATETIME NOT NULL,
  last_modify DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_modifier VARCHAR(255),
  last_check DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_message VARCHAR(255),
  report_id INT,
);

-- Create the Report table
CREATE TABLE report (
  id INT AUTO_INCREMENT PRIMARY KEY,
  type VARCHAR(255) NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  file_size FLOAT NOT NULL,
  duration FLOAT,
  resolution VARCHAR(255),
  video_codec VARCHAR(255),
  audio_tracks INT
);

-- Create the Magnet table (optional, not defined in your code)
CREATE TABLE magnet (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  link VARCHAR(255) NOT NULL
);
