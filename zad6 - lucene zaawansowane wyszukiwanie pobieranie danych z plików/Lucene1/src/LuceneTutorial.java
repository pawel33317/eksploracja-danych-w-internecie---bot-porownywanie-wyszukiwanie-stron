import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.store.IOContext;
import org.apache.lucene.store.IndexInput;
import org.apache.lucene.store.Lock;
import org.apache.lucene.store.RAMDirectory;



public class LuceneTutorial {
	public static int INDEX_COUNT = 0;
	public static int MAX_INDEX_COUNT = 500;
	public static String CURRENT_FILE = "";
	public static String PREVIOUS_BOOK = "";
	public static List<String> CURRENT_FILE_LINES;
	public static final Charset CHARSET = Charset.forName("ISO-8859-1");

	private static void addDoc(String title, String content)
			throws IOException {
		Document doc = new Document();
		doc.add(new TextField("title", title.replace("<br>", " "), Field.Store.YES));// z tokenizacją
		doc.add(new TextField("content", content, Field.Store.YES));// bez tokenizacji
		w.addDocument(doc);
	}

	/*
	 * Szuka wszystkich plików spakowanych w podkatalogach
	 * rozpakowywuje
	 * czyta je
	 * 
	 * czieli na tytuł i treść
	 * wrzuca do Lucene
	 * 
	 */
	public static void budujBazeLucene(String path) throws IOException {
		File root = new File(path);
		File[] list = root.listFiles();
		if (list == null)
			return;
		for (File f : list) {
			if (INDEX_COUNT >= MAX_INDEX_COUNT){
				break;
			}
			if (f.isDirectory()) {
				budujBazeLucene(f.getAbsolutePath());
				//System.out.println("Dir:" + f.getAbsoluteFile());
			} else {
				//System.out.println("File: " + f.getAbsoluteFile());
				UnZip unZip = new UnZip();
				String katalog = f.getAbsoluteFile().toString().substring(0, f.getAbsoluteFile().toString().lastIndexOf("\\"));
				String nazwaPliku = f.getAbsoluteFile().toString().substring(katalog.length()+1,  f.getAbsoluteFile().toString().length()-4);
				//System.out.println("==="+nazwaPliku);
		    	if(unZip.unZipIt(f.getAbsoluteFile().toString(),katalog)){
		    		//System.out.println("odpakowano");
		    		//System.out.println(f.getAbsoluteFile().toString().substring(0, f.getAbsoluteFile().toString().lastIndexOf("\\"))+"\\"+nazwaPliku+".txt");
		    		if (readFile(f.getAbsoluteFile().toString().substring(0, f.getAbsoluteFile().toString().lastIndexOf("\\"))+"\\"+nazwaPliku+".txt")){
		    			//System.out.println("znaleziono ksiazke");
		    			
		    			boolean titleFounded = false;
		    			String title = ""; 
		    				int titleFinishLine = 0;	
		    			for (int i = 0; i < 50; i++) {
		    				if (!titleFounded){
								if (CURRENT_FILE_LINES.get(i).startsWith("Title: ")){
									titleFounded = true;
									title = CURRENT_FILE_LINES.get(i);
								}
		    				}else{
		    					if (CURRENT_FILE_LINES.get(i).equals("")){
		    						titleFinishLine = i;
		    						break;
		    					}else{
		    						title = title + CURRENT_FILE_LINES.get(i);
		    					}
		    				}
		    			
						}	
		    			if (PREVIOUS_BOOK.equals(title)){
	    					continue;
		    			}
		    			for (int i = titleFinishLine; i < CURRENT_FILE_LINES.size(); i++) {
		    				int z = 0;
		    				if (i-1 > 0)
		    					z = i-1 ;
		    				if(CURRENT_FILE_LINES.get(i).equals("")||
		    						CURRENT_FILE_LINES.get(i).startsWith("Language: ")||
		    						CURRENT_FILE_LINES.get(i).startsWith("Author: ")||
		    						CURRENT_FILE_LINES.get(i).startsWith("Character ")||
		    						CURRENT_FILE_LINES.get(i).startsWith("*** START")||
		    						CURRENT_FILE_LINES.get(i).startsWith("Release Date:")||
		    						CURRENT_FILE_LINES.get(i).startsWith("[Date last ")||
		    						CURRENT_FILE_LINES.get(i).equals(" ")||
		    						CURRENT_FILE_LINES.get(i).startsWith("Last updated")||
		    						CURRENT_FILE_LINES.get(i).startsWith("Produced by ")||
		    						CURRENT_FILE_LINES.get(i).startsWith("This file was produced from ")||
		    						(CURRENT_FILE_LINES.get(z).startsWith("Produced by ")&& !CURRENT_FILE_LINES.get(i).equals(""))){
		    					titleFinishLine++;
		    				}else{
		    					break;
		    				}
		    			}
		    			PREVIOUS_BOOK = title;
		    			
		    			/////////////////////BUDOWANIE CONTENTU KSIAZKI
		    			StringBuilder sb = new StringBuilder();
		    			for (int j = titleFinishLine; j<CURRENT_FILE_LINES.size();j++) {
		    				sb.append(CURRENT_FILE_LINES.get(j));
		    			}
		    			addDoc(title, sb.toString().substring(0, 10000));
		    			System.out.println(title + ", Treść: '"+ sb.toString().substring(0, 50)+"'");
		    			
		    			
		    			
		    			
		    			INDEX_COUNT++;
		    		}
		    	}
			}
		}
	}
	
	
	
	public static boolean readFile(String fileName) throws IOException {
		try{
			List<String> lines = Files.readAllLines(Paths.get(fileName), CHARSET);
			StringBuilder sb = new StringBuilder();
			for (String s : lines) {
				sb.append(s);
			}
			CURRENT_FILE_LINES = lines;
			CURRENT_FILE =  sb.toString();
			return true;
		} catch(Exception ex){
			//ex.printStackTrace();
			return false;
		}
	}
	
	public static StandardAnalyzer analyzer;
	public static Directory ramDirectory;
	public static File f;
	public static Directory fsDirectory;
	public static IndexWriterConfig config;
	public static IndexWriter w;
	
	
	public static void search(String querystr) throws ParseException, IOException{
		System.out.println("Wszystkie strony przetworzone");
		
		Query q = new QueryParser("title", analyzer).parse(querystr);
		int hitsPerPage = 100;
		IndexReader reader = DirectoryReader.open(fsDirectory);
		IndexSearcher searcher = new IndexSearcher(reader);
		TopDocs docs = searcher.search(q, hitsPerPage);
		ScoreDoc[] hits = docs.scoreDocs;
		System.out.println("Found " + hits.length + " hits.");
		for (int i = 0; i < hits.length; ++i) {
			int docId = hits[i].doc;
			Document d = searcher.doc(docId);
			System.out.println((i + 1) + ". " + d.get("title") + "\n\t" + d.get("content").substring(0, 50));
		}
	}
	
	
	public static void main(String[] args) throws IOException, ParseException {
		analyzer = new StandardAnalyzer();
		ramDirectory = new RAMDirectory();
		f = new File("luceneDB");
		fsDirectory = FSDirectory.open(f.toPath());
		/*config = new IndexWriterConfig(analyzer);
		w = new IndexWriter(fsDirectory, config);
		budujBazeLucene("booksGUTENBERG");
		w.close();
		 */
		search(args.length > 0 ? args[0] : "british");
		
		Scanner scanner = new Scanner (System.in);
		    while (scanner.hasNext()) {
		        String searching = scanner.nextLine();
		        if (searching.equals("q"))
		        	break;
		        else
		            System.out.println("Szukane: " + searching);
		        	search(searching);
		    }
	}
}