
#include <iostream>
#include "xmlrpc-c/server_abyss.hpp"
#include "xmlrpc-c/client.hpp"

#define NAME       "XML-RPC getSumAndDifference C++ Client"
#define VERSION    "0.1"
#define SERVER_URL "http://xmlrpc-c.sourceforge.net/api/sample.php"

using std;

static void get_sum_and_difference () {

    // Build our parameter array.
    XmlRpcValue param_array = XmlRpcValue::makeArray();
    param_array.arrayAppendItem(XmlRpcValue::makeInt(5));
    param_array.arrayAppendItem(XmlRpcValue::makeInt(3));

    // Create an object to resprent the server, and make our call.
    XmlRpcClient server (SERVER_URL);
    XmlRpcValue result = server.call("sample.sumAndDifference", param_array);

    // Extract the sum and difference from our struct.
    XmlRpcValue::int32 sum = result.structGetValue("sum").getInt();
    XmlRpcValue::int32 diff = result.structGetValue("difference").getInt();
        
    cout << "Sum: " << sum << ", Difference: " << diff << endl;
}

int main (int argc, char **argv) {

    // Start up our client library.
    XmlRpcClient::Initialize(NAME, VERSION);

    // Call our client routine, and watch out for faults.
    try {
        get_sum_and_difference();
    } catch (XmlRpcFault& fault) {
        cerr << argv[0] << ": XML-RPC fault #" << fault.getFaultCode()
             << ": " << fault.getFaultString() << endl;
        XmlRpcClient::Terminate();
        exit(1);
    }

    // Shut down our client library.
    XmlRpcClient::Terminate();
    return 0;
}

