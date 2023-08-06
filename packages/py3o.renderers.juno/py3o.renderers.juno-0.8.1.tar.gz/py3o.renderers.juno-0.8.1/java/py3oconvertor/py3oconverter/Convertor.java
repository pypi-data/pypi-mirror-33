package py3oconverter;

import com.sun.star.bridge.XUnoUrlResolver;
import com.sun.star.beans.PropertyValue;
import com.sun.star.frame.XDesktop;

import java.net.MalformedURLException;

import com.sun.star.beans.XPropertySet;
import com.sun.star.bridge.XBridge;
import com.sun.star.bridge.XBridgeFactory;
import com.sun.star.comp.helper.Bootstrap;
import com.sun.star.connection.NoConnectException;
import com.sun.star.connection.XConnection;
import com.sun.star.connection.XConnector;
import com.sun.star.io.ConnectException;
import com.sun.star.lang.EventObject;
import com.sun.star.lang.XEventListener;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;
import com.sun.star.frame.XComponentLoader;
import com.sun.star.lang.XComponent;
import com.sun.star.lang.XMultiComponentFactory;
import com.sun.star.frame.XStorable;
import com.sun.star.io.IOException;
import com.sun.star.util.XCloseable;
import com.sun.star.util.CloseVetoException;
import com.sun.star.util.XRefreshable;
import com.sun.star.container.XIndexAccess;
//import com.sun.star.text.XDocumentIndex;
import com.sun.star.lang.IndexOutOfBoundsException;
import com.sun.star.lang.WrappedTargetException;
import com.sun.star.text.XDocumentIndexesSupplier;
import com.sun.star.text.XDocumentIndex;

import java.io.*;
import java.lang.*;
import java.util.Map;
import com.google.gson.*;

public class Convertor {

    private XComponentContext xRemoteContext;
    private String server_host = null;
    private String server_port = null;

    public Convertor(String server_host, String server_port) {
        xRemoteContext = null;
        this.server_host = server_host;
        this.server_port = server_port;
    }

    public void convert(String source_file_path, String target_file_path,
            String filter_name, String pdf_options, String pdf_options_types)throws ConnectException, Exception{

        XDesktop xDesktop = null;
        XComponent xComponent = null;
        
        xDesktop = connect(this.server_host, this.server_port);
        xComponent = openDocument(source_file_path, xDesktop);
        convert_document(target_file_path, filter_name, xComponent, pdf_options, pdf_options_types);
    }

    private String createUNOFileURL(String filelocation)
    {
        java.io.File newfile = new java.io.File(filelocation);
        java.net.URL before = null;
        try
        {
            // use the new toURI API because the direct toURL on a java.io.File
            // is deprecated
            before = newfile.toURI().toURL();
        }
        catch (MalformedURLException e) {
            e.printStackTrace();
        }
        // Create a URL, which can be used by UNO
        String myUNOFileURL = com.sun.star.uri.ExternalUriReferenceTranslator.create(xRemoteContext).translateToInternal(before.toExternalForm());

        if (myUNOFileURL.length() == 0 && filelocation.length() > 0)
        {
            System.out.println("File URL conversion failed. Filelocation " +
                    "contains illegal characters: " + filelocation);
        }
        return myUNOFileURL;
    }
    
    protected void refreshDocument(XComponent document) {
		XRefreshable refreshable = (XRefreshable) UnoRuntime.queryInterface(XRefreshable.class, document);
		if (refreshable != null) {
			refreshable.refresh();
		}
	}

    protected void refreshIndexes(XComponent document) {
        XDocumentIndexesSupplier indexsupplier = (XDocumentIndexesSupplier) UnoRuntime.queryInterface(XDocumentIndexesSupplier.class, document);
        if (indexsupplier != null) {
    		XIndexAccess indexaccess = indexsupplier.getDocumentIndexes();

            for (int i = 0;  i < indexaccess.getCount(); i++) {
                try {
                    XDocumentIndex index = (XDocumentIndex) UnoRuntime.queryInterface(XDocumentIndex.class, indexaccess.getByIndex(i));
                    if (index != null) {
                        index.update();
                    }
                 } catch (IndexOutOfBoundsException e) {
                    e.printStackTrace();
                 } catch (WrappedTargetException e) {
                    e.printStackTrace();
                 }
            }
        }
            
   }
    
    private void convert_document(String targetFilename, String conversionFilter, XComponent xComponent, String pdf_options, String pdf_options_types)
    {
        // How to get the XComponent, see ../Office/Office.OpenDocumentFromURL.snip
        XStorable xStorable = (XStorable)
        UnoRuntime.queryInterface(XStorable.class, xComponent);

        // refresh document
        refreshDocument(xComponent);
        // and indexes
        refreshIndexes(xComponent);

        // Set properties for conversions
        PropertyValue[] conversionProperties = new PropertyValue[3];

        conversionProperties[0] = new PropertyValue();
        conversionProperties[0].Name = "Overwrite";
        conversionProperties[0].Value = new Boolean(true);

        conversionProperties[1] = new PropertyValue();
        conversionProperties[1].Name = "FilterName";
        conversionProperties[1].Value = conversionFilter;

        Map<String, String> pdf_options_map = new Gson().fromJson(pdf_options, Map.class);
        Map<String, String> pdf_options_types_map = new Gson().fromJson(pdf_options_types, Map.class);

        PropertyValue[] aFilterData = new PropertyValue[pdf_options_map.size()];
        int i = 0;
        for (Map.Entry<String, String> entry : pdf_options_map.entrySet()) {
            String property_name = entry.getKey();
            String property_type = pdf_options_types_map.get(property_name);
            String property_value = entry.getValue();
            // System.out.println(property_name + "|" + property_value + "|" + property_type);
            aFilterData[i] = new PropertyValue();
            aFilterData[i].Name = property_name;
            if (property_type.equals("boolean") && property_value.equals("true")) {
                aFilterData[i].Value = true;
            }
            else if (property_type.equals("boolean") && property_value.equals("false")) {
                aFilterData[i].Value = false;
            }
            else if (property_type.equals("integer")) {
                aFilterData[i].Value = Integer.parseInt(property_value);
            }
            else if (property_type.equals("string")) {
                aFilterData[i].Value = property_value;
            }
            i++;
        }

        conversionProperties[2] = new PropertyValue();
        conversionProperties[2].Name = "FilterData";
        conversionProperties[2].Value = aFilterData;

        // Convert
        try {
            // See ../Office/Office.CreateUNOCompatibleURL.snip for method createUNOFileURL(targetFilename);
            xStorable.storeToURL(createUNOFileURL(targetFilename),
                    conversionProperties);

            //try to close using the latest API
            XCloseable xCloseable =
                    (XCloseable)UnoRuntime.queryInterface(XCloseable.class, xStorable);

            if ( xCloseable != null ) {
                try{
                    xCloseable.close(false);
                } catch (CloseVetoException e) {
                    // do nothing
                }
            } else {
                // the close API was not implemented, we just dipose()
                xComponent.dispose();
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    private XComponent openDocument(String source_file_path, XDesktop xDesktop) {
        XComponentLoader xComponentLoader = (XComponentLoader)
        UnoRuntime.queryInterface(XComponentLoader.class, xDesktop);

        PropertyValue[] myProperties = new PropertyValue[1];
        myProperties[0] = new PropertyValue();
        myProperties[0].Name = "Hidden";
        // for open document and do not show user interface use "true"
        myProperties[0].Value = new Boolean(true);

        XComponent xComponent = null;
        // Load a given document
        try	{
            String source_file_url = createUNOFileURL(source_file_path);
            xComponent = xComponentLoader.loadComponentFromURL(
                    source_file_url, "_blank", 0, myProperties);
        }
        catch(Exception e) {
            e.printStackTrace();
        }

        return xComponent;
    }

	private XDesktop connect(String host, String port) throws ConnectException, Exception{
        XMultiComponentFactory xRemoteServiceManager = null;
        XDesktop xDesktop = null;
        
        try {
          // connect and retrieve a remote service manager and component context
          XComponentContext xLocalContext =
              com.sun.star.comp.helper.Bootstrap.createInitialComponentContext(null);

          XMultiComponentFactory xLocalServiceManager = xLocalContext.getServiceManager();

          Object urlResolver = xLocalServiceManager.createInstanceWithContext(
              "com.sun.star.bridge.UnoUrlResolver", xLocalContext );

          XUnoUrlResolver xUnoUrlResolver = (XUnoUrlResolver) UnoRuntime.queryInterface( 
              XUnoUrlResolver.class, urlResolver);

          Object initialObject = xUnoUrlResolver.resolve( 
              "uno:socket,host=" + host + ",port=" + port + ";urp;StarOffice.ServiceManager");

          XPropertySet xPropertySet = (XPropertySet)UnoRuntime.queryInterface(
              XPropertySet.class, initialObject);

          Object context = xPropertySet.getPropertyValue("DefaultContext"); 

          this.xRemoteContext = (XComponentContext)UnoRuntime.queryInterface(
              XComponentContext.class, context);

          xRemoteServiceManager = this.xRemoteContext.getServiceManager();

          // get Desktop instance
          Object desktop = xRemoteServiceManager.createInstanceWithContext (
              "com.sun.star.frame.Desktop", this.xRemoteContext);

          xDesktop = (XDesktop)UnoRuntime.queryInterface(XDesktop.class, desktop);
            
        } catch (NoConnectException connectException) {
            throw new ConnectException(
                    "connection failed for host: "+ host +
                    ", and port: " + port + " : " + connectException.getMessage());

        } catch (Exception exception) {
            throw new Exception("Open office exception : " + exception);
        }

        return xDesktop;
		
	}
	
	
}
