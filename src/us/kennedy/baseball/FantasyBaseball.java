//The MIT License (MIT)
//
//Copyright (c) 2010 Thomas Kennedy
//
//Permission is hereby granted, free of charge, to any person obtaining a copy
//of this software and associated documentation files (the "Software"), to deal
//in the Software without restriction, including without limitation the rights
//to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//copies of the Software, and to permit persons to whom the Software is
//furnished to do so, subject to the following conditions:
//
//The above copyright notice and this permission notice shall be included in all
//copies or substantial portions of the Software.
//
//THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//SOFTWARE.

package us.kennedy.baseball;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * This class takes a text file with Last Name, First Name (e.g Kennedy, Tom)
 * and changes it to First Initial Last Name (e.g. T Kennedy). It also removes
 * any lines that begin with BATTER or PITCHER. It will remove any number of
 * spaces between fields and replace them with a single tab.
 * 
 * @author Tom Kennedy
 * @version 1.0
 */
public class FantasyBaseball {

	/**
	 * This method takes a text file with Last Name, First Name (e.g Kennedy,
	 * Tom) and changes it to First Initial Last Name (e.g. T Kennedy). It also
	 * removes any lines that begin with BATTER or PITCHER. It will remove any
	 * number of spaces between fields and replace them with a single tab.
	 * 
	 * @param args
	 *            The files that are to be parsed in the order of, args[0]
	 *            should be the document with the batters and args[1] should be
	 *            the document with the pitchers.
	 * @throws IOException
	 *             Thrown if there is a problem reading or writing files.
	 */
	public static void main(String[] args) throws IOException {
		if (args.length != 2) {
			System.out.println("You must include the name of the file");
			throw new IllegalArgumentException(
					"You must include the name of the file");
		}
		File outputFile = new File("c:\\batters.txt");
		for (int i = 0; i < args.length; i++) {
			BufferedReader reader = null;
			BufferedWriter writer = null;
			try {
				File file = new File(args[i]);
				FileReader fileReader = new FileReader(file);
				reader = new BufferedReader(fileReader);
				String line;
				String newLine;
				String tabbedLine;
				FileWriter fileWriter = new FileWriter(outputFile);
				writer = new BufferedWriter(fileWriter);
				while ((line = reader.readLine()) != null) {
					if (!line.startsWith("BATTER")
							&& !line.startsWith("PITCHER")) {
						newLine = removeSpaces(line);
						tabbedLine = addTabs(newLine);
						String batterLine = renamePlayer(tabbedLine);
						writer.append(batterLine);
						writer.newLine();
						writer.flush();
					}
				}
				outputFile = new File("c:\\pitchers.txt");
			} finally {
				if (reader != null) {
					reader.close();
				}
				if (reader != null) {
					writer.close();
				}
			}
		}
	}

	/**
	 * This method renames a player from LASTNAME, FIRSTNAME to FIRSTINITIAL
	 * LASTNAME.
	 * 
	 * @param line
	 *            The input line as it is being read.
	 * @return A player from LASTNAME, FIRSTNAME to FIRSTINITIAL LASTNAME.
	 */
	private static String renamePlayer(String line) {
		String regex = "([A-Za-z-/.' \u0009]+), ([A-Za-z-/.' ]+)(\u0009.+)";
		Pattern pattern = Pattern.compile(regex);
		if (line.matches(regex)) {

			Matcher matcher = pattern.matcher(line);
			matcher.find();
			String deLaRosa = matcher.group(1).replaceAll("\u0009", "");
			return matcher.group(2).charAt(0) + "\u0009" + deLaRosa
					+ matcher.group(3);
		}
		return line;
	}

	/**
	 * Adds tabs to every space that isnt preceded by a comma.
	 * 
	 * @param line
	 *            The line of input as it is being read.
	 * @return The line of the file with spaces replaced with tabs.
	 */
	private static String addTabs(String line) {
		if (line.contains(" ")) {
			String newLine = line.replaceAll(", ", ",");
			String tabbedLine = newLine.replaceAll(" ", "\u0009");
			String commaLine = tabbedLine.replaceFirst(",", ", ");
			return commaLine;
		}
		return line;
	}

	/**
	 * Removes all instances of multiple spaces.
	 * 
	 * @param line
	 *            The line of input as it is being read.
	 * @return The line of input with the instance of multiple spaces removed.
	 */
	private static String removeSpaces(String line) {
		if (line.contains("  ")) {
			String newLine = line.replaceAll("  ", " ");
			return removeSpaces(newLine);
		}
		return line;
	}
}
