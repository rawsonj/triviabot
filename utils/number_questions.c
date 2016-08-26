/*
 * number_questions.c
 *
 * Adds a sequence of numbers to triviabot question files
 *
 * Copyright 2016 Andy <andyqwerty@users.sourceforge.net>
 *
 * This file is part of triviabot
 * https://github.com/rawsonj/triviabot
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>

#define VERSION 1.0
#define DATE 2016-08-26

int
main (int argc, char **argv)
{

  FILE *fin, *fout;

  DIR *qdir;

  struct dirent *qfile;

  /* this program can be in any path, but must be run from inside
   * the questions directory
   */
  qdir = opendir (".");

  unsigned int q_num = 0;

  /* get the filename from each file in the /questions directory
   */
  while ((qfile = readdir (qdir)) != NULL)
  {
    /* Ignore "." and ".." files
     */
    if (strlen (qfile->d_name) <= 2)
      continue;

    fin = fopen (qfile->d_name, "r");
    printf ("%s\n", qfile->d_name);

    char q_file_path[PATH_MAX];

    strcpy (q_file_path, "./");
    strcat (q_file_path, qfile->d_name);
    strcat (q_file_path, ".new");
    strcat (q_file_path, "\0");

    fout = fopen (q_file_path, "w");
    printf ("%s\n", q_file_path);

    char line[512];
    if (fin == NULL || fout == NULL)
      perror ("Error: opening file");

    /* Read each line from the file
     */
    while (fgets (line, 512, fin) != NULL)
    {
      if (strlen (line) > 3)
        fprintf (fout, "[ %06d ] %s", ++q_num, line);
    }

    /* print an EOF at the end of every file
     */
    fprintf (fout, "%d", EOF);

    if (fclose (fin) == EOF || fclose (fout) == EOF)
      perror ("error closing file");

  }

  return 0;
}
