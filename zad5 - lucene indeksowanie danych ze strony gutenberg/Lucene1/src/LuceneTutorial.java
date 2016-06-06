import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
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
	private static List<String> getlinkList() {
		List<String> linkList = new ArrayList<String>();
		int index = "a".codePointAt(0);
		while (index <= "z".codePointAt(0)) {
			linkList.add("https://www.gutenberg.org/browse/titles/" + (char) index);
			index++;
		}
		linkList.add("https://www.gutenberg.org/browse/titles/other");
		return linkList;
	}

	private static String getUrlSource(String url) throws IOException {
		URL _url = new URL(url);
		URLConnection yc = _url.openConnection();
		BufferedReader in = new BufferedReader(new InputStreamReader(yc.getInputStream(), "UTF-8"));
		String inputLine;
		StringBuilder a = new StringBuilder();
		while ((inputLine = in.readLine()) != null)
			a.append(inputLine);
		in.close();
		return a.toString();
	}
	private static void addDoc(IndexWriter w, String title, String author, String link, String country) throws IOException {
		Document doc = new Document();
		doc.add(new TextField("title", title.replace("<br>", " "), Field.Store.YES));//z tokenizacją
		doc.add(new StringField("author", author, Field.Store.YES));//bez tokenizacji
		doc.add(new StringField("link", link, Field.Store.YES));//bez tokenizacji
		doc.add(new StringField("country", country, Field.Store.YES));//bez tokenizacji
		w.addDocument(doc);
	}
	public static void main(String[] args) throws IOException, ParseException {
		List<String> linkList = getlinkList();
		StandardAnalyzer analyzer = new StandardAnalyzer();
		Directory ramDirectory = new RAMDirectory();
		File f = new File("luceneDB");
		Directory fsDirectory = FSDirectory.open(f.toPath());
		/*IndexWriterConfig config = new IndexWriterConfig(analyzer);
		IndexWriter w = new IndexWriter(fsDirectory, config);
		int booksCounter = 0;
		for (String link : linkList){
			System.out.println("Przetwarzanie strony: "+link);
			String linkContent = getUrlSource(link);
			Pattern pattern = Pattern.compile(
					"<h2><a href=\"/ebooks/(.+?)\">(.+?)</a>(.+?)</h2><p>by <a href=\"/browse/authors/(.+?)\">(.+?)</a></p>");
			Matcher matcher = pattern.matcher(linkContent);
			while (matcher.find()) {
				addDoc(w, matcher.group(2), matcher.group(5), matcher.group(1), matcher.group(3));
				//System.out.println(matcher.group(0));// Całe wyrażenie
				//System.out.println(matcher.group(1));// Link do książki
				//System.out.println(matcher.group(2));// Tytuł
				//System.out.println(matcher.group(3));// Kraj
				//System.out.println(matcher.group(4));// Link do autora
				//System.out.println(matcher.group(5));// Autor 
				booksCounter++;
			}
			System.out.println("Ilość książek: " + ++booksCounter);
		}
		w.close();*/
		System.out.println("Wszystkie strony przetworzone");
		String querystr = args.length > 0 ? args[0] : "devil";
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
			System.out.println((i + 1) + ". " + d.get("title") + "\t\t" + d.get("author") + "\t\t" + d.get("country"));
		}
	}
}