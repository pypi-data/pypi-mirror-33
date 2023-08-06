package py3oconverter;
import com.sun.star.frame.XDesktop;
import com.sun.star.lang.XComponent;
import com.sun.star.io.ConnectException;

public class Launch {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
        String port = "8997";
        String host = "localhost";
		Convertor c = new Convertor(host, port);

        String source_file_path = "py3o_example.odt";
        String target_file_path = "toto.pdf";
        String filter_name = "writer_pdf_Export";
        String pdf_options = "";
        String pdf_options_types = "";

        try{
            c.convert(
                source_file_path,
                target_file_path,
                filter_name,
                pdf_options,
                pdf_options_types);
            System.out.println("Conversion done");

        }
        catch(ConnectException e)
        {
            e.printStackTrace();
        }
        catch(Exception e)
        {
            e.printStackTrace();
        }
        System.exit(0);

	}
}
